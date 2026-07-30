from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.enums import StatusBarril, TipoMovimentacao
from app.db.models.barril import Barril
from app.db.models.movimentacao import Movimentacao
from app.schemas.barril import BarrilCreate, BarrilUpdate


class BarrilNaoEncontradoError(Exception):
    pass


class CodigoBarrilDuplicadoError(Exception):
    pass


class BarrilPersistenciaError(Exception):
    pass


def buscar_barril_por_id(
    db: Session,
    barril_id: int,
) -> Barril | None:
    return db.get(
        Barril,
        barril_id,
    )


def buscar_barril_por_codigo(
    db: Session,
    codigo: str,
) -> Barril | None:
    comando = select(Barril).where(
        Barril.codigo == codigo
    )

    return db.scalar(comando)


def listar_barris(
    db: Session,
    offset: int = 0,
    limite: int = 100,
    status: StatusBarril | None = None,
) -> list[Barril]:
    comando = select(Barril).order_by(
        Barril.codigo
    )

    if status is not None:
        comando = comando.where(
            Barril.status == status
        )

    comando = comando.offset(offset).limit(limite)

    return list(
        db.scalars(comando).all()
    )


def obter_barril(
    db: Session,
    barril_id: int,
) -> Barril:
    barril = buscar_barril_por_id(
        db=db,
        barril_id=barril_id,
    )

    if barril is None:
        raise BarrilNaoEncontradoError(
            "Barril não encontrado."
        )

    return barril


def criar_barril(
    db: Session,
    dados: BarrilCreate,
    usuario_id: int,
) -> Barril:
    barril_existente = buscar_barril_por_codigo(
        db=db,
        codigo=dados.codigo,
    )

    if barril_existente is not None:
        raise CodigoBarrilDuplicadoError(
            "Já existe um barril cadastrado com este código."
        )

    barril = Barril(
        **dados.model_dump(),
        status=StatusBarril.DISPONIVEL,
        cliente_atual_id=None,
    )

    try:
        db.add(barril)
        db.flush()

        movimentacao_inicial = Movimentacao(
            barril_id=barril.id,
            cliente_id=None,
            usuario_id=usuario_id,
            tipo=TipoMovimentacao.ENTRADA_ESTOQUE,
            observacao=(
                "Cadastro inicial do barril no estoque."
            ),
        )

        db.add(movimentacao_inicial)

        db.commit()
        db.refresh(barril)

        return barril

    except IntegrityError as erro:
        db.rollback()

        raise CodigoBarrilDuplicadoError(
            "Já existe um barril cadastrado com este código."
        ) from erro

    except SQLAlchemyError as erro:
        db.rollback()

        raise BarrilPersistenciaError(
            "Não foi possível cadastrar o barril."
        ) from erro


def atualizar_barril(
    db: Session,
    barril_id: int,
    dados: BarrilUpdate,
) -> Barril:
    barril = obter_barril(
        db=db,
        barril_id=barril_id,
    )

    alteracoes = dados.model_dump(
        exclude_unset=True
    )

    codigo = alteracoes.get("codigo")

    if codigo is not None:
        barril_existente = buscar_barril_por_codigo(
            db=db,
            codigo=codigo,
        )

        if (
            barril_existente is not None
            and barril_existente.id != barril.id
        ):
            raise CodigoBarrilDuplicadoError(
                "Já existe um barril cadastrado com este código."
            )

    for campo, valor in alteracoes.items():
        setattr(
            barril,
            campo,
            valor,
        )

    try:
        db.commit()
        db.refresh(barril)

        return barril

    except IntegrityError as erro:
        db.rollback()

        raise CodigoBarrilDuplicadoError(
            "Já existe um barril cadastrado com este código."
        ) from erro

    except SQLAlchemyError as erro:
        db.rollback()

        raise BarrilPersistenciaError(
            "Não foi possível atualizar o barril."
        ) from erro