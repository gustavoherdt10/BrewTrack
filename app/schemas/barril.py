from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.core.enums import StatusBarril

CapacidadeBarril = Literal[15, 30, 50]


class BarrilBase(BaseModel):
    codigo: str = Field(
        min_length=3,
        max_length=50,
    )

    capacidade_litros: CapacidadeBarril

    data_aquisicao: date | None = None

    observacao: str | None = None

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo(cls, codigo: str) -> str:
        return codigo.strip().upper()


class BarrilCreate(BarrilBase):
    pass


class BarrilUpdate(BaseModel):
    codigo: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    capacidade_litros: CapacidadeBarril | None = None

    data_aquisicao: date | None = None

    observacao: str | None = None

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo(
        cls,
        codigo: str | None,
    ) -> str | None:
        if codigo is None:
            return None

        return codigo.strip().upper()


class BarrilRead(BarrilBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusBarril
    cliente_atual_id: int | None
    criado_em: datetime
    atualizado_em: datetime
