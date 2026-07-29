from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cliente import (
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
)
from app.services.cliente_service import (
    ClienteNaoEncontradoError,
    ClientePersistenciaError,
    DocumentoClienteDuplicadoError,
    atualizar_cliente,
    criar_cliente,
    listar_clientes,
    obter_cliente,
)

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ClienteRead,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_cliente(
    dados: ClienteCreate,
    db: DatabaseSession,
) -> ClienteRead:
    try:
        return criar_cliente(
            db=db,
            dados=dados,
        )

    except DocumentoClienteDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro

    except ClientePersistenciaError as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro


@router.get(
    "",
    response_model=list[ClienteRead],
)
def consultar_clientes(
    db: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 100,
    ativo: Annotated[bool | None, Query()] = None,
) -> list[ClienteRead]:
    return listar_clientes(
        db=db,
        offset=offset,
        limite=limite,
        ativo=ativo,
    )


@router.get(
    "/{cliente_id}",
    response_model=ClienteRead,
)
def consultar_cliente(
    cliente_id: Annotated[int, Path(gt=0)],
    db: DatabaseSession,
) -> ClienteRead:
    try:
        return obter_cliente(
            db=db,
            cliente_id=cliente_id,
        )

    except ClienteNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro


@router.patch(
    "/{cliente_id}",
    response_model=ClienteRead,
)
def editar_cliente(
    cliente_id: Annotated[int, Path(gt=0)],
    dados: ClienteUpdate,
    db: DatabaseSession,
) -> ClienteRead:
    try:
        return atualizar_cliente(
            db=db,
            cliente_id=cliente_id,
            dados=dados,
        )

    except ClienteNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except DocumentoClienteDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro

    except ClientePersistenciaError as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro
