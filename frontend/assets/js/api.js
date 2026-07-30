import { API_BASE_URL } from "./config.js";
import {
    encerrarSessao,
    obterToken,
} from "./session.js";


const LOGIN_URL = new URL(
    "../../index.html",
    import.meta.url,
).href;


export class ApiError extends Error {
    constructor(message, status = 0, details = null) {
        super(message);

        this.name = "ApiError";
        this.status = status;
        this.details = details;
    }
}


async function lerResposta(response) {
    const contentType =
        response.headers.get("content-type") ?? "";

    if (contentType.includes("application/json")) {
        return response.json();
    }

    const texto = await response.text();

    if (!texto) {
        return null;
    }

    return {
        detail: texto,
    };
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
            .map((erro) => erro.msg ?? "Dado inválido.")
            .join(" ");
    }

    return `A requisição falhou com status ${status}.`;
}


export async function apiFetch(
    endpoint,
    options = {},
) {
    const token = obterToken();
    const headers = new Headers(options.headers ?? {});

    if (!headers.has("Accept")) {
        headers.set("Accept", "application/json");
    }

    const possuiCorpo =
        options.body !== undefined &&
        options.body !== null;

    const corpoEhFormData =
        typeof FormData !== "undefined" &&
        options.body instanceof FormData;

    if (
        possuiCorpo &&
        !corpoEhFormData &&
        !headers.has("Content-Type")
    ) {
        headers.set(
            "Content-Type",
            "application/json",
        );
    }

    if (token) {
        headers.set(
            "Authorization",
            `Bearer ${token}`,
        );
    }

    let response;

    try {
        response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,
                headers,
            },
        );
    } catch {
        throw new ApiError(
            "Não foi possível conectar ao servidor.",
        );
    }

    const data = await lerResposta(response);

    if (response.status === 401) {
        encerrarSessao();

        const estaNaPaginaLogin =
            window.location.pathname.endsWith(
                "/index.html",
            ) ||
            window.location.pathname.endsWith("/");

        if (!estaNaPaginaLogin) {
            window.location.href = LOGIN_URL;
        }
    }

    if (!response.ok) {
        throw new ApiError(
            extrairMensagemErro(
                data,
                response.status,
            ),
            response.status,
            data,
        );
    }

    return data;
}