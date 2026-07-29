from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import gerar_hash_senha
from app.db.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate


class UsuarioDuplicadoError(Exception):
    pass


class UsuarioNaoEncontradoError(Exception):
    pass


def buscar_usuario_por_email(
    db: Session,
    email: str,
) -> Usuario | None:
    email_normalizado = email.strip().lower()

    statement = select(Usuario).where(func.lower(Usuario.email) == email_normalizado)

    return db.scalar(statement)


def buscar_usuario_por_id(
    db: Session,
    usuario_id: int,
) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def listar_usuarios(
    db: Session,
    offset: int = 0,
    limite: int = 100,
) -> list[Usuario]:
    statement = select(Usuario).order_by(Usuario.id).offset(offset).limit(limite)

    return list(db.scalars(statement).all())


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
        raise UsuarioDuplicadoError("Já existe um usuário cadastrado com este e-mail.")

    senha_hash = gerar_hash_senha(dados.senha)

    usuario = Usuario(
        nome=dados.nome.strip(),
        email=email_normalizado,
        senha_hash=senha_hash,
        perfil=dados.perfil,
        ativo=True,
    )

    try:
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    except IntegrityError as erro:
        db.rollback()

        raise UsuarioDuplicadoError(
            "Não foi possível cadastrar o usuário porque os dados já existem."
        ) from erro

    return usuario
