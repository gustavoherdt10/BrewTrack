from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get(
    "/health",
    summary="Verificar funcionamento da API",
)
def verificar_api() -> dict[str, str]:
    return {
        "status": "ok",
        "aplicacao": "BrewTrack API",
    }


@router.get(
    "/health/database",
    summary="Verificar conexão com o PostgreSQL",
)
def verificar_banco(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "conectado",
        }

    except SQLAlchemyError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível.",
        ) from erro
