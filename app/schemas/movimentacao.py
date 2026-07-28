from datetime import date, datetime, timezone

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.enums import TipoMovimentacao


class MovimentacaoBase(BaseModel):
    barril_id: int = Field(gt=0)

    cliente_id: int | None = Field(
        default=None,
        gt=0,
    )

    usuario_id: int = Field(gt=0)

    tipo: TipoMovimentacao

    data_movimentacao: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    data_prevista_retorno: date | None = None

    responsavel_recebimento: str | None = Field(
        default=None,
        max_length=120,
    )

    observacao: str | None = None

    @model_validator(mode="after")
    def validar_cliente_obrigatorio(
        self,
    ) -> "MovimentacaoBase":
        tipos_com_cliente = {
            TipoMovimentacao.SAIDA_CLIENTE,
            TipoMovimentacao.RETORNO_CLIENTE,
        }

        if self.tipo in tipos_com_cliente and self.cliente_id is None:
            raise ValueError(
                "O cliente é obrigatório para saída ou retorno de cliente."
            )

        return self


class MovimentacaoCreate(MovimentacaoBase):
    pass


class MovimentacaoRead(MovimentacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
