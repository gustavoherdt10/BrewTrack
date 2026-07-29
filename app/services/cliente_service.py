from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteNaoEncontradoError(Exception):
    pass


class DocumentoClienteDuplicadoError(Exception):
    pass


class ClientePersistenciaError(Exception):
    pass


def buscar_cliente_por_id(
    db: Session,
    cliente_id: int,
) -> Cliente | None:
    return db.get(Cliente, cliente_id)


def buscar_cliente_por_documento(
    db: Session,
    documento: str,
) -> Cliente | None:
    comando = select(Cliente).where(Cliente.documento == documento)

    return db.scalar(comando)


def listar_clientes(
    db: Session,
    offset: int = 0,
    limite: int = 100,
    ativo: bool | None = None,
) -> list[Cliente]:
    comando = select(Cliente).order_by(Cliente.nome_razao_social)

    if ativo is not None:
        comando = comando.where(Cliente.ativo == ativo)

    comando = comando.offset(offset).limit(limite)

    return list(db.scalars(comando).all())


def obter_cliente(
    db: Session,
    cliente_id: int,
) -> Cliente:
    cliente = buscar_cliente_por_id(
        db=db,
        cliente_id=cliente_id,
    )

    if cliente is None:
        raise ClienteNaoEncontradoError("Cliente não encontrado.")

    return cliente


def criar_cliente(
    db: Session,
    dados: ClienteCreate,
) -> Cliente:
    if dados.documento is not None:
        cliente_existente = buscar_cliente_por_documento(
            db=db,
            documento=dados.documento,
        )

        if cliente_existente is not None:
            raise DocumentoClienteDuplicadoError(
                "Já existe um cliente cadastrado com este documento."
            )

    cliente = Cliente(**dados.model_dump())

    try:
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

        return cliente

    except IntegrityError as erro:
        db.rollback()

        raise DocumentoClienteDuplicadoError(
            "Já existe um cliente cadastrado com este documento."
        ) from erro

    except SQLAlchemyError as erro:
        db.rollback()

        raise ClientePersistenciaError("Não foi possível salvar o cliente.") from erro


def atualizar_cliente(
    db: Session,
    cliente_id: int,
    dados: ClienteUpdate,
) -> Cliente:
    cliente = obter_cliente(
        db=db,
        cliente_id=cliente_id,
    )

    alteracoes = dados.model_dump(exclude_unset=True)
    documento = alteracoes.get("documento")

    if documento is not None:
        cliente_existente = buscar_cliente_por_documento(
            db=db,
            documento=documento,
        )

        if cliente_existente is not None and cliente_existente.id != cliente.id:
            raise DocumentoClienteDuplicadoError(
                "Já existe um cliente cadastrado com este documento."
            )

    for campo, valor in alteracoes.items():
        setattr(cliente, campo, valor)

    try:
        db.commit()
        db.refresh(cliente)

        return cliente

    except IntegrityError as erro:
        db.rollback()

        raise DocumentoClienteDuplicadoError(
            "Já existe um cliente cadastrado com este documento."
        ) from erro

    except SQLAlchemyError as erro:
        db.rollback()

        raise ClientePersistenciaError(
            "Não foi possível atualizar o cliente."
        ) from erro
