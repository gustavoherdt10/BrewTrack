from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoPessoa
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.movimentacao import Movimentacao


class Cliente(TimestampMixin, Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)

    tipo_pessoa: Mapped[TipoPessoa] = mapped_column(
        SqlEnum(
            TipoPessoa,
            name="tipo_pessoa_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    nome_razao_social: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
        index=True,
    )

    nome_fantasia: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )

    documento: Mapped[str | None] = mapped_column(
        String(18),
        nullable=True,
        unique=True,
    )

    telefone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(180),
        nullable=True,
    )

    logradouro: Mapped[str | None] = mapped_column(
        String(180),
        nullable=True,
    )

    numero: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    complemento: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bairro: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    cidade: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    estado: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    cep: Mapped[str | None] = mapped_column(
        String(9),
        nullable=True,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    movimentacoes: Mapped[list[Movimentacao]] = relationship(
        back_populates="cliente",
        passive_deletes=True,
    )
