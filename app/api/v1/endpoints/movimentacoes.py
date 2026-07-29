from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.enums import TipoMovimentacao
from app.db.session import get_db
from app.schemas.movimentacao import (
    MovimentacaoCreate,
    MovimentacaoRead,
)
from app.services.movimentacao_service import (
    BarrilMovimentacaoNaoEncontradoError,
    ClienteMovimentacaoInativoError,
    ClienteMovimentacaoNaoEncontradoError,
    MovimentacaoConflitoError,
    MovimentacaoPersistenciaError,
    UsuarioMovimentacaoInativoError,
    UsuarioMovimentacaoNaoEncontradoError,
    criar_movimentacao,
    listar_movimentacoes,
)

router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=MovimentacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimentacao(
    dados: MovimentacaoCreate,
    db: DatabaseSession,
) -> MovimentacaoRead:
    try:
        return criar_movimentacao(
            db=db,
            dados=dados,
        )

    except (
        BarrilMovimentacaoNaoEncontradoError,
        ClienteMovimentacaoNaoEncontradoError,
        UsuarioMovimentacaoNaoEncontradoError,
    ) as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except (
        UsuarioMovimentacaoInativoError,
        ClienteMovimentacaoInativoError,
        MovimentacaoConflitoError,
    ) as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro

    except MovimentacaoPersistenciaError as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro


@router.get(
    "",
    response_model=list[MovimentacaoRead],
)
def consultar_movimentacoes(
    db: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 100,
    barril_id: Annotated[int | None, Query(gt=0)] = None,
    cliente_id: Annotated[int | None, Query(gt=0)] = None,
    tipo: Annotated[
        TipoMovimentacao | None,
        Query(),
    ] = None,
) -> list[MovimentacaoRead]:
    return listar_movimentacoes(
        db=db,
        offset=offset,
        limite=limite,
        barril_id=barril_id,
        cliente_id=cliente_id,
        tipo=tipo,
    )
