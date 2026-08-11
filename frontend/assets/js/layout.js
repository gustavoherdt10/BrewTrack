import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import {
    encerrarSessao,
    obterToken,
    obterUsuario,
    salvarUsuario,
} from "./session.js";
import { mostrarAlerta } from "./ui.js";

const LOGIN_URL = new URL("../../index.html", import.meta.url).href;
const sidebar = document.querySelector("#app-sidebar");
const overlay = document.querySelector("#sidebar-overlay");
const alertaGlobal = document.querySelector("#alerta-global");

function perfilEhAdministrador(perfil) {
    return ["ADMIN", "ADMINISTRADOR"].includes(String(perfil ?? "").toUpperCase());
}

function obterIniciais(nome) {
    const partes = String(nome ?? "BrewTrack")
        .trim()
        .split(/\s+/)
        .filter(Boolean);

    if (!partes.length) {
        return "BT";
    }

    const primeira = partes[0][0] ?? "B";
    const ultima = partes.length > 1 ? partes.at(-1)[0] : partes[0][1] ?? "T";
    return `${primeira}${ultima}`.toUpperCase();
}

function preencherUsuario(usuario) {
    if (!usuario) {
        return;
    }

    document.querySelectorAll("[data-user-name]").forEach((elemento) => {
        elemento.textContent = usuario.nome ?? "Usuário";
    });

    document.querySelectorAll("[data-user-profile]").forEach((elemento) => {
        elemento.textContent = usuario.perfil ?? "Sem perfil";
    });

    document.querySelectorAll("[data-user-profile-detail]").forEach((elemento) => {
        elemento.textContent = usuario.perfil ?? "—";
    });

    document.querySelectorAll("[data-user-id]").forEach((elemento) => {
        elemento.textContent = usuario.id ?? "—";
    });

    document.querySelectorAll("[data-user-email]").forEach((elemento) => {
        elemento.textContent = usuario.email ?? "—";
    });

    document.querySelectorAll("[data-user-initials]").forEach((elemento) => {
        elemento.textContent = obterIniciais(usuario.nome);
    });

    document.querySelectorAll("[data-admin-only]").forEach((elemento) => {
        elemento.hidden = !perfilEhAdministrador(usuario.perfil);
    });
}

function marcarNavegacaoAtiva() {
    const pagina = document.body.dataset.page;

    document.querySelectorAll("[data-nav-page]").forEach((link) => {
        link.classList.toggle("active", link.dataset.navPage === pagina);
        if (link.dataset.navPage === pagina) {
            link.setAttribute("aria-current", "page");
        }
    });
}

function abrirSidebar() {
    sidebar?.classList.add("is-open");
    overlay?.classList.add("is-visible");
    document.body.style.overflow = "hidden";
}

function fecharSidebar() {
    sidebar?.classList.remove("is-open");
    overlay?.classList.remove("is-visible");
    document.body.style.overflow = "";
}

function configurarEventos() {
    document.querySelectorAll("[data-sidebar-open]").forEach((botao) => {
        botao.addEventListener("click", abrirSidebar);
    });

    document.querySelectorAll("[data-sidebar-close]").forEach((botao) => {
        botao.addEventListener("click", fecharSidebar);
    });

    document.querySelectorAll(".app-nav-link").forEach((link) => {
        link.addEventListener("click", fecharSidebar);
    });

    document.querySelectorAll("[data-logout]").forEach((botao) => {
        botao.addEventListener("click", () => {
            encerrarSessao();
            window.location.replace(LOGIN_URL);
        });
    });

    window.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            fecharSidebar();
        }
    });
}

async function verificarSessao() {
    if (!obterToken()) {
        window.location.replace(LOGIN_URL);
        return;
    }

    const usuarioLocal = obterUsuario();
    preencherUsuario(usuarioLocal);

    try {
        const usuarioAtual = await apiFetch(API_ROUTES.usuarioAtual);
        salvarUsuario(usuarioAtual);
        preencherUsuario(usuarioAtual);
        document.dispatchEvent(new CustomEvent("brewtrack:usuario-carregado", {
            detail: usuarioAtual,
        }));
    } catch (erro) {
        if (erro.status !== 401) {
            mostrarAlerta(
                alertaGlobal,
                erro.message ?? "Não foi possível validar a sessão atual.",
            );
        }
    }
}

function inicializar() {
    document.querySelectorAll("[data-current-year]").forEach((elemento) => {
        elemento.textContent = String(new Date().getFullYear());
    });

    marcarNavegacaoAtiva();
    configurarEventos();
    verificarSessao();
}

inicializar();