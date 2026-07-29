# BrewTrack API

Backend do protótipo BrewTrack, desenvolvido para o Trabalho de
Conclusão de Curso em Sistemas de Informação.

O sistema tem como objetivo apoiar o controle de estoque, o rastreamento
e o registro das movimentações de barris em microcervejarias.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Alembic
- Psycopg 3

## Preparação do ambiente

Criar o ambiente virtual:

```powershell
py -m venv .venv

Rodar o Servidor

```powershell
uvicorn app.main:app --reload