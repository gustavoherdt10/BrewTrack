from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

from app.core.jwt_config import get_jwt_settings

password_hasher = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    return password_hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return password_hasher.verify(
            senha_hash,
            senha,
        )
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False


def hash_precisa_atualizacao(senha_hash: str) -> bool:
    try:
        return password_hasher.check_needs_rehash(senha_hash)
    except InvalidHashError:
        return False


def criar_access_token(usuario_id: int) -> tuple[str, int]:
    settings = get_jwt_settings()

    agora = datetime.now(timezone.utc)

    expiracao = agora + timedelta(
        minutes=settings.jwt_access_token_expire_minutes,
    )

    payload = {
        "sub": str(usuario_id),
        "type": "access",
        "iat": agora,
        "exp": expiracao,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    expires_in = settings.jwt_access_token_expire_minutes * 60

    return token, expires_in


def decodificar_access_token(token: str) -> int:
    settings = get_jwt_settings()

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": [
                "sub",
                "exp",
                "iat",
                "type",
            ]
        },
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido.")

    try:
        return int(payload["sub"])
    except (TypeError, ValueError) as erro:
        raise jwt.InvalidTokenError("Identificador do usuário inválido.") from erro
