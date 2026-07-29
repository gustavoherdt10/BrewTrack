import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.core.enums import TipoPessoa


def somente_digitos(valor: str | None) -> str | None:
    if valor is None:
        return None

    valor_normalizado = re.sub(r"\D", "", valor)

    return valor_normalizado or None


class ClienteBase(BaseModel):
    tipo_pessoa: TipoPessoa

    nome_razao_social: str = Field(
        min_length=2,
        max_length=160,
    )

    nome_fantasia: str | None = Field(
        default=None,
        max_length=160,
    )

    documento: str | None = Field(
        default=None,
        max_length=18,
    )

    telefone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    logradouro: str | None = Field(
        default=None,
        max_length=180,
    )

    numero: str | None = Field(
        default=None,
        max_length=20,
    )

    complemento: str | None = Field(
        default=None,
        max_length=100,
    )

    bairro: str | None = Field(
        default=None,
        max_length=100,
    )

    cidade: str | None = Field(
        default=None,
        max_length=100,
    )

    estado: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        pattern=r"^[A-Z]{2}$",
    )

    cep: str | None = Field(
        default=None,
        max_length=9,
    )

    ativo: bool = True

    @field_validator("documento", mode="before")
    @classmethod
    def normalizar_documento(
        cls,
        valor: str | None,
    ) -> str | None:
        return somente_digitos(valor)

    @field_validator("cep", mode="before")
    @classmethod
    def normalizar_cep(
        cls,
        valor: str | None,
    ) -> str | None:
        return somente_digitos(valor)

    @field_validator("estado", mode="before")
    @classmethod
    def normalizar_estado(
        cls,
        valor: str | None,
    ) -> str | None:
        if valor is None:
            return None

        return valor.strip().upper()


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    tipo_pessoa: TipoPessoa | None = None

    nome_razao_social: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    nome_fantasia: str | None = Field(
        default=None,
        max_length=160,
    )

    documento: str | None = Field(
        default=None,
        max_length=18,
    )

    telefone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    logradouro: str | None = Field(
        default=None,
        max_length=180,
    )

    numero: str | None = Field(
        default=None,
        max_length=20,
    )

    complemento: str | None = Field(
        default=None,
        max_length=100,
    )

    bairro: str | None = Field(
        default=None,
        max_length=100,
    )

    cidade: str | None = Field(
        default=None,
        max_length=100,
    )

    estado: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        pattern=r"^[A-Z]{2}$",
    )

    cep: str | None = Field(
        default=None,
        max_length=9,
    )

    ativo: bool | None = None

    @field_validator("documento", mode="before")
    @classmethod
    def normalizar_documento(
        cls,
        valor: str | None,
    ) -> str | None:
        return somente_digitos(valor)

    @field_validator("cep", mode="before")
    @classmethod
    def normalizar_cep(
        cls,
        valor: str | None,
    ) -> str | None:
        return somente_digitos(valor)

    @field_validator("estado", mode="before")
    @classmethod
    def normalizar_estado(
        cls,
        valor: str | None,
    ) -> str | None:
        if valor is None:
            return None

        return valor.strip().upper()


class ClienteRead(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
    atualizado_em: datetime
