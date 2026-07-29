"""Adiciona cliente atual ao barril.

Revision ID: 42a66e79cfe7
Revises: 2a1dd9751bd9
Create Date: 2026-07-29 11:35:18.504802
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "42a66e79cfe7"
down_revision: str | Sequence[str] | None = "2a1dd9751bd9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona cliente atual ao barril e limita as capacidades."""

    # A convenção do projeto adicionará automaticamente:
    # ck_barris_capacidade_litros_positiva
    op.drop_constraint(
        "capacidade_litros_positiva",
        "barris",
        type_="check",
    )

    # O nome gerado no PostgreSQL será:
    # ck_barris_capacidade_litros_permitida
    op.create_check_constraint(
        "capacidade_litros_permitida",
        "barris",
        "capacidade_litros IN (15, 30, 50)",
    )

    op.add_column(
        "barris",
        sa.Column(
            "cliente_atual_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_barris_cliente_atual_id",
        "barris",
        ["cliente_atual_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_barris_cliente_atual_id_clientes",
        "barris",
        "clientes",
        ["cliente_atual_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Remove cliente atual e restaura a regra anterior."""

    op.drop_constraint(
        "fk_barris_cliente_atual_id_clientes",
        "barris",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_barris_cliente_atual_id",
        table_name="barris",
    )

    op.drop_column(
        "barris",
        "cliente_atual_id",
    )

    # A convenção localizará:
    # ck_barris_capacidade_litros_permitida
    op.drop_constraint(
        "capacidade_litros_permitida",
        "barris",
        type_="check",
    )

    # Restaura:
    # ck_barris_capacidade_litros_positiva
    op.create_check_constraint(
        "capacidade_litros_positiva",
        "barris",
        "capacidade_litros > 0",
    )