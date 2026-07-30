from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.api.dependencies import (
    DatabaseSession,
    exigir_perfis,
)
from app.core.enums import (
    PerfilUsuario,
    TipoMovimentacao,
)
from app.db.models.usuario import Usuario
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
    criar_movimentacao,
    listar_movimentacoes,
)

router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"],
)


UsuarioOperacionalAtual = Annotated[
    Usuario,
    Depends(
        exigir_perfis(
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.OPERADOR,
        )
    ),
]


UsuarioLeituraAtual = Annotated[
    Usuario,
    Depends(
        exigir_perfis(
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.OPERADOR,
            PerfilUsuario.CONSULTA,
        )
    ),
]


@router.post(
    "",
    response_model=MovimentacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimentacao(
    dados: MovimentacaoCreate,
    db: DatabaseSession,
    usuario_atual: UsuarioOperacionalAtual,
) -> MovimentacaoRead:
    try:
        return criar_movimentacao(
            db=db,
            dados=dados,
            usuario_id=usuario_atual.id,
        )

    except (
        BarrilMovimentacaoNaoEncontradoError,
        ClienteMovimentacaoNaoEncontradoError,
    ) as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except (
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
    _usuario_atual: UsuarioLeituraAtual,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limite: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 100,
    barril_id: Annotated[
        int | None,
        Query(gt=0),
    ] = None,
    cliente_id: Annotated[
        int | None,
        Query(gt=0),
    ] = None,
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