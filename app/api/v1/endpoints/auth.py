from fastapi import APIRouter

from app.api.dependencies import (
    CurrentUser,
    DatabaseSession,
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.usuario import UsuarioResponse
from app.services.auth_service import autenticar_usuario

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    dados: LoginRequest,
    db: DatabaseSession,
) -> TokenResponse:
    _usuario, token, expires_in = autenticar_usuario(
        db=db,
        email=str(dados.email),
        senha=dados.senha,
    )

    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
    )


@router.get(
    "/me",
    response_model=UsuarioResponse,
)
def consultar_usuario_logado(
    usuario_atual: CurrentUser,
) -> UsuarioResponse:
    return usuario_atual
