from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import PerfilUsuario
from app.core.exceptions import (
    ConflitoError,
    RecursoNaoEncontradoError,
)
from app.core.security import gerar_hash_senha
from app.db.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
)


def buscar_usuario_por_email(
    db: Session,
    email: str,
    ignorar_usuario_id: int | None = None,
) -> Usuario | None:
    email_normalizado = email.strip().lower()

    statement = select(Usuario).where(func.lower(Usuario.email) == email_normalizado)

    if ignorar_usuario_id is not None:
        statement = statement.where(Usuario.id != ignorar_usuario_id)

    return db.scalar(statement)


def buscar_usuario_por_id(
    db: Session,
    usuario_id: int,
) -> Usuario | None:
    return db.get(
        Usuario,
        usuario_id,
    )


def obter_usuario_por_id(
    db: Session,
    usuario_id: int,
) -> Usuario:
    usuario = buscar_usuario_por_id(
        db,
        usuario_id,
    )

    if usuario is None:
        raise RecursoNaoEncontradoError("Usuário não encontrado.")

    return usuario


def listar_usuarios(
    db: Session,
    offset: int = 0,
    limite: int = 100,
) -> list[Usuario]:
    statement = select(Usuario).order_by(Usuario.id).offset(offset).limit(limite)

    return list(db.scalars(statement).all())


def contar_administradores_ativos(
    db: Session,
) -> int:
    statement = select(func.count(Usuario.id)).where(
        Usuario.perfil == PerfilUsuario.ADMINISTRADOR,
        Usuario.ativo.is_(True),
    )

    quantidade = db.scalar(statement)

    return int(quantidade or 0)


def criar_usuario(
    db: Session,
    dados: UsuarioCreate,
) -> Usuario:
    email_normalizado = str(dados.email).strip().lower()

    usuario_existente = buscar_usuario_por_email(
        db,
        email_normalizado,
    )

    if usuario_existente is not None:
        raise ConflitoError("Já existe um usuário cadastrado com este e-mail.")

    usuario = Usuario(
        nome=dados.nome.strip(),
        email=email_normalizado,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=dados.perfil,
        ativo=dados.ativo,
    )

    try:
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    except IntegrityError as erro:
        db.rollback()

        raise ConflitoError(
            "Não foi possível cadastrar o usuário porque os dados já existem."
        ) from erro

    return usuario


def atualizar_usuario(
    db: Session,
    usuario_id: int,
    dados: UsuarioUpdate,
) -> Usuario:
    usuario = obter_usuario_por_id(
        db,
        usuario_id,
    )

    alteracoes = dados.model_dump(exclude_unset=True)

    if not alteracoes:
        return usuario

    novo_email = alteracoes.get("email")

    if novo_email is not None:
        email_normalizado = str(novo_email).strip().lower()

        usuario_com_mesmo_email = buscar_usuario_por_email(
            db,
            email_normalizado,
            ignorar_usuario_id=usuario.id,
        )

        if usuario_com_mesmo_email is not None:
            raise ConflitoError("Já existe outro usuário cadastrado com este e-mail.")

        alteracoes["email"] = email_normalizado

    novo_nome = alteracoes.get("nome")

    if novo_nome is not None:
        alteracoes["nome"] = novo_nome.strip()

    usuario_eh_administrador_ativo = (
        usuario.perfil == PerfilUsuario.ADMINISTRADOR and usuario.ativo
    )

    novo_perfil = alteracoes.get(
        "perfil",
        usuario.perfil,
    )

    novo_status_ativo = alteracoes.get(
        "ativo",
        usuario.ativo,
    )

    deixara_de_ser_administrador_ativo = (
        novo_perfil != PerfilUsuario.ADMINISTRADOR or novo_status_ativo is False
    )

    if usuario_eh_administrador_ativo and deixara_de_ser_administrador_ativo:
        quantidade_administradores = contar_administradores_ativos(db)

        if quantidade_administradores <= 1:
            raise ConflitoError(
                "Não é possível desativar ou alterar "
                "o perfil do último administrador "
                "ativo do sistema."
            )

    senha_nova = alteracoes.pop(
        "senha",
        None,
    )

    if senha_nova is not None:
        usuario.senha_hash = gerar_hash_senha(senha_nova)

    for campo, valor in alteracoes.items():
        setattr(
            usuario,
            campo,
            valor,
        )

    try:
        db.commit()
        db.refresh(usuario)

    except IntegrityError as erro:
        db.rollback()

        raise ConflitoError(
            "Não foi possível atualizar o usuário "
            "porque os dados informados já existem."
        ) from erro

    return usuario
