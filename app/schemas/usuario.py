from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.core.enums import PerfilUsuario


class UsuarioBase(BaseModel):
    nome: str = Field(
        min_length=3,
        max_length=120,
    )

    email: EmailStr

    perfil: PerfilUsuario = PerfilUsuario.OPERADOR

    ativo: bool = True

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(cls, nome: str) -> str:
        return nome.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, email: str) -> str:
        return email.strip().lower()


class UsuarioCreate(UsuarioBase):
    senha: str = Field(
        min_length=8,
        max_length=128,
    )


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=3,
        max_length=120,
    )

    email: EmailStr | None = None

    senha: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    perfil: PerfilUsuario | None = None

    ativo: bool | None = None

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(
        cls,
        nome: str | None,
    ) -> str | None:
        if nome is None:
            return None

        return nome.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(
        cls,
        email: str | None,
    ) -> str | None:
        if email is None:
            return None

        return email.strip().lower()


class UsuarioResponse(UsuarioBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    criado_em: datetime
    atualizado_em: datetime


UsuarioRead = UsuarioResponse
