from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, email: str) -> str:
        return email.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
