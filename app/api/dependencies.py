from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.enums import PerfilUsuario
from app.core.exceptions import (
    AutenticacaoError,
    PermissaoNegadaError,
)
from app.core.security import decodificar_access_token
from app.db.models.usuario import Usuario
from app.db.session import get_db

bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer",
    description=("Informe apenas o token JWT retornado por /api/v1/auth/login."),
    auto_error=False,
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_current_user(
    db: DatabaseSession,
    credenciais: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> Usuario:
    erro_credenciais = AutenticacaoError(
        "Token ausente, inválido ou expirado.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if credenciais is None:
        raise erro_credenciais

    if credenciais.scheme.lower() != "bearer":
        raise erro_credenciais

    try:
        usuario_id = decodificar_access_token(credenciais.credentials)
    except jwt.InvalidTokenError as erro:
        raise erro_credenciais from erro

    usuario = db.get(
        Usuario,
        usuario_id,
    )

    if usuario is None:
        raise erro_credenciais

    if not usuario.ativo:
        raise AutenticacaoError(
            "O usuário está inativo.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return usuario


CurrentUser = Annotated[
    Usuario,
    Depends(get_current_user),
]


def exigir_perfis(
    *perfis_permitidos: PerfilUsuario,
) -> Callable[..., Usuario]:
    def dependencia(
        usuario_atual: CurrentUser,
    ) -> Usuario:
        if usuario_atual.perfil not in perfis_permitidos:
            raise PermissaoNegadaError(
                "Seu perfil não possui permissão para esta operação."
            )

        return usuario_atual

    return dependencia
