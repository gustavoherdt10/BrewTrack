from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.core.enums import StatusBarril


class BarrilBase(BaseModel):
    codigo: str = Field(
        min_length=3,
        max_length=50,
    )

    capacidade_litros: int = Field(
        gt=0,
    )

    status: StatusBarril = StatusBarril.DISPONIVEL

    data_aquisicao: date | None = None

    observacao: str | None = None

    @field_validator("codigo")
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

    capacidade_litros: int | None = Field(
        default=None,
        gt=0,
    )

    status: StatusBarril | None = None

    data_aquisicao: date | None = None

    observacao: str | None = None

    @field_validator("codigo")
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
    criado_em: datetime
    atualizado_em: datetime
