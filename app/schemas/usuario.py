from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import PerfilUsuario


class UsuarioBase(BaseModel):
    nome: str = Field(
        min_length=3,
        max_length=120,
    )

    email: EmailStr

    perfil: PerfilUsuario = PerfilUsuario.OPERADOR

    ativo: bool = True


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


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
    atualizado_em: datetime
