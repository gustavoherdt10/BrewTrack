import { API_BASE_URL } from "./config.js";
import { encerrarSessao, obterToken } from "./session.js";

const LOGIN_URL = new URL("../../index.html", import.meta.url).href;

export class ApiError extends Error {
    constructor(message, status = 0, details = null) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.details = details;
    }
}

async function lerResposta(response) {
    if (response.status === 204) {
        return null;
    }

    const contentType = response.headers.get("content-type") ?? "";

    if (contentType.includes("application/json")) {
        const texto = await response.text();
        return texto ? JSON.parse(texto) : null;
    }

    const texto = await response.text();
    return texto ? { detail: texto } : null;
}

function extrairMensagemErro(data, status) {
    if (!data) {
        return `A requisição falhou com status ${status}.`;
    }

    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.detail)) {
        return data.detail
            .map((erro) => {
                const local = Array.isArray(erro.loc)
                    ? erro.loc.filter((item) => item !== "body").join(".")
                    : "";
                const mensagem = erro.msg ?? "Dado inválido.";
                return local ? `${local}: ${mensagem}` : mensagem;
            })
            .join(" ");
    }

    if (typeof data.message === "string") {
        return data.message;
    }

    return `A requisição falhou com status ${status}.`;
}

export async function apiFetch(endpoint, options = {}) {
    const {
        auth = true,
        headers: customHeaders,
        ...fetchOptions
    } = options;

    const token = obterToken();
    const headers = new Headers(customHeaders ?? {});

    if (!headers.has("Accept")) {
        headers.set("Accept", "application/json");
    }

    const possuiCorpo = fetchOptions.body !== undefined && fetchOptions.body !== null;
    const corpoEhFormData = typeof FormData !== "undefined" && fetchOptions.body instanceof FormData;

    if (possuiCorpo && !corpoEhFormData && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    if (auth && token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    let response;

    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...fetchOptions,
            headers,
        });
    } catch {
        throw new ApiError(
            "Não foi possível conectar ao backend. Confirme se o Uvicorn está rodando em http://127.0.0.1:8000.",
        );
    }

    let data;

    try {
        data = await lerResposta(response);
    } catch {
        throw new ApiError(
            "A API retornou uma resposta que não pôde ser interpretada.",
            response.status,
        );
    }

    if (response.status === 401 && auth) {
        encerrarSessao();

        const estaNaPaginaLogin =
            window.location.pathname.endsWith("/index.html") ||
            window.location.pathname.endsWith("/");

        if (!estaNaPaginaLogin) {
            window.location.replace(LOGIN_URL);
        }
    }

    if (!response.ok) {
        throw new ApiError(
            extrairMensagemErro(data, response.status),
            response.status,
            data,
        );
    }

    return data;
}