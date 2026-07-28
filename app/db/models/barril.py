from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import StatusBarril
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.movimentacao import Movimentacao


class Barril(TimestampMixin, Base):
    __tablename__ = "barris"

    __table_args__ = (
        CheckConstraint(
            "capacidade_litros > 0",
            name="capacidade_litros_positiva",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    codigo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    capacidade_litros: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[StatusBarril] = mapped_column(
        SqlEnum(
            StatusBarril,
            name="status_barril_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=StatusBarril.DISPONIVEL,
        server_default=StatusBarril.DISPONIVEL.value,
        nullable=False,
        index=True,
    )

    data_aquisicao: Mapped[date | None] = mapped_column(
        nullable=True,
    )

    observacao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    movimentacoes: Mapped[list[Movimentacao]] = relationship(
        back_populates="barril",
        passive_deletes=True,
    )
