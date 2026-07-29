from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.enums import TipoMovimentacao


class MovimentacaoCreate(BaseModel):
    barril_id: int = Field(gt=0)

    cliente_id: int | None = Field(
        default=None,
        gt=0,
    )

    usuario_id: int = Field(gt=0)

    tipo: TipoMovimentacao

    data_prevista_retorno: date | None = None

    responsavel_recebimento: str | None = Field(
        default=None,
        max_length=120,
    )

    observacao: str | None = None

    @model_validator(mode="after")
    def validar_movimentacao(self) -> "MovimentacaoCreate":
        tipos_implementados = {
            TipoMovimentacao.SAIDA_CLIENTE,
            TipoMovimentacao.RETORNO_CLIENTE,
        }

        if self.tipo not in tipos_implementados:
            raise ValueError(
                "Nesta etapa são permitidas somente SAIDA_CLIENTE e RETORNO_CLIENTE."
            )

        if self.cliente_id is None:
            raise ValueError("O cliente é obrigatório para saída ou retorno.")

        return self


class MovimentacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    barril_id: int
    cliente_id: int | None
    usuario_id: int
    tipo: TipoMovimentacao
    data_movimentacao: datetime
    data_prevista_retorno: date | None
    responsavel_recebimento: str | None
    observacao: str | None
    criado_em: datetime
