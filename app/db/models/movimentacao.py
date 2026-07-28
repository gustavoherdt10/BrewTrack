from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoMovimentacao
from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.db.models.barril import Barril
    from app.db.models.cliente import Cliente
    from app.db.models.usuario import Usuario


class Movimentacao(CreatedAtMixin, Base):
    __tablename__ = "movimentacoes"

    __table_args__ = (
        CheckConstraint(
            (
                "tipo NOT IN "
                "('SAIDA_CLIENTE', 'RETORNO_CLIENTE') "
                "OR cliente_id IS NOT NULL"
            ),
            name="cliente_obrigatorio_saida_retorno",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    barril_id: Mapped[int] = mapped_column(
        ForeignKey(
            "barris.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "clientes.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tipo: Mapped[TipoMovimentacao] = mapped_column(
        SqlEnum(
            TipoMovimentacao,
            name="tipo_movimentacao_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        index=True,
    )

    data_movimentacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    data_prevista_retorno: Mapped[date | None] = mapped_column(
        nullable=True,
    )

    responsavel_recebimento: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    observacao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    barril: Mapped[Barril] = relationship(
        back_populates="movimentacoes",
    )

    cliente: Mapped[Cliente | None] = relationship(
        back_populates="movimentacoes",
    )

    usuario: Mapped[Usuario] = relationship(
        back_populates="movimentacoes",
    )
