from getpass import getpass

from app.core.enums import PerfilUsuario
from app.db.session import SessionLocal
from app.schemas.usuario import UsuarioCreate
from app.services.usuario_service import criar_usuario


def main() -> None:
    print("Criação do primeiro administrador do BrewTrack")

    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()

    senha = getpass("Senha (mínimo 8 caracteres): ")

    with SessionLocal() as db:
        usuario = criar_usuario(
            db,
            UsuarioCreate(
                nome=nome,
                email=email,
                senha=senha,
                perfil=PerfilUsuario.ADMINISTRADOR,
                ativo=True,
            ),
        )

    print(f"Administrador criado com ID {usuario.id}.")


if __name__ == "__main__":
    main()
