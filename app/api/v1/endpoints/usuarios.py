from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from app.api.dependencies import (
    DatabaseSession,
    exigir_perfis,
)
from app.core.enums import PerfilUsuario
from app.db.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.services.usuario_service import (
    atualizar_usuario,
    criar_usuario,
    listar_usuarios,
    obter_usuario_por_id,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)


AdministradorAtual = Annotated[
    Usuario,
    Depends(exigir_perfis(PerfilUsuario.ADMINISTRADOR)),
]


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(
    dados: UsuarioCreate,
    db: DatabaseSession,
    _administrador: AdministradorAtual,
) -> Usuario:
    return criar_usuario(
        db,
        dados,
    )


@router.get(
    "",
    response_model=list[UsuarioResponse],
)
def consultar_usuarios(
    db: DatabaseSession,
    _administrador: AdministradorAtual,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limite: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 100,
) -> list[Usuario]:
    return listar_usuarios(
        db,
        offset=offset,
        limite=limite,
    )


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
)
def consultar_usuario_por_id(
    usuario_id: int,
    db: DatabaseSession,
    _administrador: AdministradorAtual,
) -> Usuario:
    return obter_usuario_por_id(
        db,
        usuario_id,
    )


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioResponse,
)
def alterar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: DatabaseSession,
    _administrador: AdministradorAtual,
) -> Usuario:
    return atualizar_usuario(
        db,
        usuario_id,
        dados,
    )
