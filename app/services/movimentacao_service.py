from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.enums import (
    StatusBarril,
    TipoMovimentacao,
)
from app.db.models.barril import Barril
from app.db.models.cliente import Cliente
from app.db.models.movimentacao import Movimentacao
from app.schemas.movimentacao import MovimentacaoCreate


class BarrilMovimentacaoNaoEncontradoError(Exception):
    pass


class ClienteMovimentacaoNaoEncontradoError(Exception):
    pass


class ClienteMovimentacaoInativoError(Exception):
    pass


class MovimentacaoConflitoError(Exception):
    pass


class MovimentacaoPersistenciaError(Exception):
    pass


def listar_movimentacoes(
    db: Session,
    offset: int = 0,
    limite: int = 100,
    barril_id: int | None = None,
    cliente_id: int | None = None,
    tipo: TipoMovimentacao | None = None,
) -> list[Movimentacao]:
    comando = select(Movimentacao)

    if barril_id is not None:
        comando = comando.where(
            Movimentacao.barril_id == barril_id
        )

    if cliente_id is not None:
        comando = comando.where(
            Movimentacao.cliente_id == cliente_id
        )

    if tipo is not None:
        comando = comando.where(
            Movimentacao.tipo == tipo
        )

    comando = (
        comando
        .order_by(
            Movimentacao.data_movimentacao.desc(),
            Movimentacao.id.desc(),
        )
        .offset(offset)
        .limit(limite)
    )

    return list(
        db.scalars(comando).all()
    )


def criar_movimentacao(
    db: Session,
    dados: MovimentacaoCreate,
    usuario_id: int,
) -> Movimentacao:
    try:
        comando_barril = (
            select(Barril)
            .where(
                Barril.id == dados.barril_id
            )
            .with_for_update()
        )

        barril = db.scalar(comando_barril)

        if barril is None:
            raise BarrilMovimentacaoNaoEncontradoError(
                "Barril não encontrado."
            )

        if dados.cliente_id is None:
            raise ClienteMovimentacaoNaoEncontradoError(
                "Cliente não informado."
            )

        cliente = db.get(
            Cliente,
            dados.cliente_id,
        )

        if cliente is None:
            raise ClienteMovimentacaoNaoEncontradoError(
                "Cliente não encontrado."
            )

        if dados.tipo == TipoMovimentacao.SAIDA_CLIENTE:
            if not cliente.ativo:
                raise ClienteMovimentacaoInativoError(
                    "Não é possível enviar um barril "
                    "para um cliente inativo."
                )

            if (
                barril.status != StatusBarril.DISPONIVEL
                or barril.cliente_atual_id is not None
            ):
                raise MovimentacaoConflitoError(
                    "O barril não está disponível para saída."
                )

            barril.status = StatusBarril.COM_CLIENTE
            barril.cliente_atual_id = cliente.id

        elif dados.tipo == TipoMovimentacao.RETORNO_CLIENTE:
            if barril.status != StatusBarril.COM_CLIENTE:
                raise MovimentacaoConflitoError(
                    "O barril não está registrado como "
                    "estando com cliente."
                )

            if barril.cliente_atual_id != cliente.id:
                raise MovimentacaoConflitoError(
                    "O cliente informado não corresponde "
                    "ao cliente atual do barril."
                )

            barril.status = StatusBarril.DISPONIVEL
            barril.cliente_atual_id = None

        else:
            raise MovimentacaoConflitoError(
                "Tipo de movimentação ainda não implementado."
            )

        movimentacao = Movimentacao(
            **dados.model_dump(),
            usuario_id=usuario_id,
        )

        db.add(movimentacao)
        db.commit()
        db.refresh(movimentacao)

        return movimentacao

    except (
        BarrilMovimentacaoNaoEncontradoError,
        ClienteMovimentacaoNaoEncontradoError,
        ClienteMovimentacaoInativoError,
        MovimentacaoConflitoError,
    ):
        db.rollback()
        raise

    except SQLAlchemyError as erro:
        db.rollback()

        raise MovimentacaoPersistenciaError(
            "Não foi possível registrar a movimentação."
        ) from erro