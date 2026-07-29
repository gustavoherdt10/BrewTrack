from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    barris,
    usuarios,
    clientes,
    movimentacoes,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(usuarios.router)
api_router.include_router(clientes.router)
api_router.include_router(barris.router)
api_router.include_router(movimentacoes.router)