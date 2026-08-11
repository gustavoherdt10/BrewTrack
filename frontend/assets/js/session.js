const TOKEN_KEY = "brewtrack_access_token";
const USER_KEY = "brewtrack_usuario";
const SAVED_EMAIL_KEY = "brewtrack_email_lembrado";

export function salvarToken(token) {
    if (typeof token !== "string" || !token.trim()) {
        throw new Error("Token inválido.");
    }

    sessionStorage.setItem(TOKEN_KEY, token);
}

export function obterToken() {
    return sessionStorage.getItem(TOKEN_KEY);
}

export function salvarUsuario(usuario) {
    if (!usuario || typeof usuario !== "object") {
        throw new Error("Dados do usuário inválidos.");
    }

    sessionStorage.setItem(USER_KEY, JSON.stringify(usuario));
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

export function salvarEmailLembrado(email) {
    if (email) {
        localStorage.setItem(SAVED_EMAIL_KEY, email);
        return;
    }

    localStorage.removeItem(SAVED_EMAIL_KEY);
}

export function obterEmailLembrado() {
    return localStorage.getItem(SAVED_EMAIL_KEY) ?? "";
}