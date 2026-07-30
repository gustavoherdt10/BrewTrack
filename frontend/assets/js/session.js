const TOKEN_KEY = "brewtrack_access_token";
const USER_KEY = "brewtrack_usuario";


export function salvarToken(token) {
    if (!token) {
        throw new Error("Token inválido.");
    }

    sessionStorage.setItem(TOKEN_KEY, token);
}


export function obterToken() {
    return sessionStorage.getItem(TOKEN_KEY);
}


export function salvarUsuario(usuario) {
    if (!usuario) {
        throw new Error("Dados do usuário inválidos.");
    }

    sessionStorage.setItem(
        USER_KEY,
        JSON.stringify(usuario),
    );
}


export function obterUsuario() {
    const usuarioSalvo = sessionStorage.getItem(USER_KEY);

    if (!usuarioSalvo) {
        return null;
    }

    try {
        return JSON.parse(usuarioSalvo);
    } catch {
        sessionStorage.removeItem(USER_KEY);
        return null;
    }
}


export function possuiSessao() {
    return Boolean(obterToken());
}


export function encerrarSessao() {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
}