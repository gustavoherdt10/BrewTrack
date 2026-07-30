from datetime import date, datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.enums import TipoMovimentacao


class MovimentacaoCampos(BaseModel):
    barril_id: int = Field(gt=0)

    cliente_id: int | None = Field(
        default=None,
        gt=0,
    )

    tipo: TipoMovimentacao

    data_prevista_retorno: date | None = None

    responsavel_recebimento: str | None = Field(
        default=None,
        max_length=120,
    )

    observacao: str | None = None


class MovimentacaoCreate(MovimentacaoCampos):
    @model_validator(mode="after")
    def validar_movimentacao_manual(self) -> Self:
        tipos_permitidos = {
            TipoMovimentacao.SAIDA_CLIENTE,
            TipoMovimentacao.RETORNO_CLIENTE,
        }

        if self.tipo not in tipos_permitidos:
            raise ValueError(
                "Nesta etapa, o registro manual permite apenas "
                "SAIDA_CLIENTE e RETORNO_CLIENTE."
            )

        if self.cliente_id is None:
            raise ValueError(
                "O cliente é obrigatório para saída ou retorno."
            )

        return self


class MovimentacaoRead(MovimentacaoCampos):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    data_movimentacao: datetime
    criado_em: datetime