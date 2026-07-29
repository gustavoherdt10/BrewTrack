from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BrewTrackError


def registrar_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BrewTrackError)
    async def tratar_erro_brewtrack(
        _request: Request,
        erro: BrewTrackError,
    ) -> JSONResponse:
        conteudo: dict[str, object] = {
            "erro": erro.codigo,
            "mensagem": erro.mensagem,
            "status": erro.status_code,
        }

        if erro.contexto:
            conteudo["contexto"] = erro.contexto

        return JSONResponse(
            status_code=erro.status_code,
            content=conteudo,
            headers=erro.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def tratar_erro_validacao(
        _request: Request,
        erro: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "erro": "dados_invalidos",
                "mensagem": "Os dados enviados são inválidos.",
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detalhes": erro.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def tratar_http_exception(
        _request: Request,
        erro: StarletteHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=erro.status_code,
            content={
                "erro": "erro_http",
                "mensagem": str(erro.detail),
                "status": erro.status_code,
            },
            headers=erro.headers,
        )
