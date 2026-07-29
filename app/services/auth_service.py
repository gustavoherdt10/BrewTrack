from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AutenticacaoError
from app.core.security import (
    criar_access_token,
    gerar_hash_senha,
    hash_precisa_atualizacao,
    verificar_senha,
)
from app.db.models.usuario import Usuario


def autenticar_usuario(
    db: Session,
    email: str,
    senha: str,
) -> tuple[Usuario, str, int]:
    comando = select(Usuario).where(func.lower(Usuario.email) == email.lower())

    usuario = db.scalar(comando)

    erro_login = AutenticacaoError(
        "E-mail ou senha inválidos.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if usuario is None:
        raise erro_login

    if not verificar_senha(
        senha,
        usuario.senha_hash,
    ):
        raise erro_login

    if not usuario.ativo:
        raise AutenticacaoError(
            "O usuário está inativo.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if hash_precisa_atualizacao(usuario.senha_hash):
        usuario.senha_hash = gerar_hash_senha(senha)
        db.commit()

    token, expires_in = criar_access_token(usuario.id)

    return usuario, token, expires_in
