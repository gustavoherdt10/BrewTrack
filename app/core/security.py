from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro da senha recebida.

    A senha original nunca deve ser armazenada no banco de dados.
    """
    return password_hash.hash(senha)


def verificar_senha(
    senha: str,
    senha_hash: str,
) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return password_hash.verify(
        senha,
        senha_hash,
    )