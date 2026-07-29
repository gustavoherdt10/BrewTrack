from typing import Any

from fastapi import status


class BrewTrackError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    codigo = "erro_de_negocio"

    def __init__(
        self,
        mensagem: str,
        *,
        headers: dict[str, str] | None = None,
        contexto: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(mensagem)

        self.mensagem = mensagem
        self.headers = headers
        self.contexto = contexto


class AutenticacaoError(BrewTrackError):
    status_code = status.HTTP_401_UNAUTHORIZED
    codigo = "nao_autenticado"


class PermissaoNegadaError(BrewTrackError):
    status_code = status.HTTP_403_FORBIDDEN
    codigo = "permissao_negada"


class RecursoNaoEncontradoError(BrewTrackError):
    status_code = status.HTTP_404_NOT_FOUND
    codigo = "recurso_nao_encontrado"


class ConflitoError(BrewTrackError):
    status_code = status.HTTP_409_CONFLICT
    codigo = "conflito"


class PersistenciaError(BrewTrackError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    codigo = "erro_de_persistencia"
