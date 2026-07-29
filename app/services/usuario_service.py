from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
    statement = select(Usuario).where(Usuario.email == email)

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
    statement = (
        select(Usuario)
        .order_by(Usuario.id)
        .offset(offset)
        .limit(limite)
    )

    return list(db.scalars(statement).all())


def criar_usuario(
    db: Session,
    dados: UsuarioCreate,
    senha_hash: str,
) -> Usuario:
    usuario_existente = buscar_usuario_por_email(db, dados.email)

    if usuario_existente is not None:
        raise UsuarioDuplicadoError(
            "Já existe um usuário cadastrado com este e-mail."
        )

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
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