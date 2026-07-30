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
    StatusBarril,
)
from app.db.models.usuario import Usuario
from app.schemas.barril import (
    BarrilCreate,
    BarrilRead,
    BarrilUpdate,
)
from app.services.barril_service import (
    BarrilNaoEncontradoError,
    BarrilPersistenciaError,
    CodigoBarrilDuplicadoError,
    atualizar_barril,
    criar_barril,
    listar_barris,
    obter_barril,
)

router = APIRouter(
    prefix="/barris",
    tags=["Barris"],
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
    response_model=BarrilRead,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_barril(
    dados: BarrilCreate,
    db: DatabaseSession,
    usuario_atual: UsuarioOperacionalAtual,
) -> BarrilRead:
    try:
        return criar_barril(
            db=db,
            dados=dados,
            usuario_id=usuario_atual.id,
        )

    except CodigoBarrilDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro

    except BarrilPersistenciaError as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro


@router.get(
    "",
    response_model=list[BarrilRead],
)
def consultar_barris(
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
    status_barril: Annotated[
        StatusBarril | None,
        Query(alias="status"),
    ] = None,
) -> list[BarrilRead]:
    return listar_barris(
        db=db,
        offset=offset,
        limite=limite,
        status=status_barril,
    )


@router.get(
    "/{barril_id}",
    response_model=BarrilRead,
)
def consultar_barril(
    barril_id: int,
    db: DatabaseSession,
    _usuario_atual: UsuarioLeituraAtual,
) -> BarrilRead:
    try:
        return obter_barril(
            db=db,
            barril_id=barril_id,
        )

    except BarrilNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro


@router.patch(
    "/{barril_id}",
    response_model=BarrilRead,
)
def editar_barril(
    barril_id: int,
    dados: BarrilUpdate,
    db: DatabaseSession,
    _usuario_atual: UsuarioOperacionalAtual,
) -> BarrilRead:
    try:
        return atualizar_barril(
            db=db,
            barril_id=barril_id,
            dados=dados,
        )

    except BarrilNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except CodigoBarrilDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro

    except BarrilPersistenciaError as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro