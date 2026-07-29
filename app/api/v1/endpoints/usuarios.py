from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import gerar_hash_senha
from app.db.session import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services.usuario_service import (
    UsuarioDuplicadoError,
    criar_usuario,
    listar_usuarios,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(
    dados: UsuarioCreate,
    db: DatabaseSession,
) -> UsuarioResponse:
    try:
        senha_hash = gerar_hash_senha(dados.senha)

        return criar_usuario(
            db=db,
            dados=dados,
            senha_hash=senha_hash,
        )
    except UsuarioDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro


@router.get(
    "",
    response_model=list[UsuarioResponse],
)
def consultar_usuarios(
    db: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[UsuarioResponse]:
    return listar_usuarios(
        db=db,
        offset=offset,
        limite=limite,
    )
