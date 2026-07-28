from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PerfilUsuario
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.movimentacao import Movimentacao


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
        unique=True,
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    perfil: Mapped[PerfilUsuario] = mapped_column(
        SqlEnum(
            PerfilUsuario,
            name="perfil_usuario_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=PerfilUsuario.OPERADOR,
        server_default=PerfilUsuario.OPERADOR.value,
        nullable=False,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    movimentacoes: Mapped[list[Movimentacao]] = relationship(
        back_populates="usuario",
        passive_deletes=True,
    )
