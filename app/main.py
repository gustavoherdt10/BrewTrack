from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=("API para gestão de estoque, rastreamento e movimentação de barris."),
)


@app.get(
    "/",
    tags=["Raiz"],
    summary="Apresentar informações da API",
)
def raiz() -> dict[str, str]:
    return {
        "aplicacao": settings.app_name,
        "versao": settings.app_version,
        "documentacao": "/docs",
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)
