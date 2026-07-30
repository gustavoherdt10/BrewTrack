import { apiFetch } from "./api.js";
import {
    encerrarSessao,
    obterToken,
    salvarUsuario,
} from "./session.js";


const LOGIN_URL = new URL(
    "../../index.html",
    import.meta.url,
).href;


const nomeUsuario = document.querySelector(
    "#nome-usuario",
);

const perfilUsuario = document.querySelector(
    "#perfil-usuario",
);

const idUsuario = document.querySelector(
    "#id-usuario",
);

const emailUsuario = document.querySelector(
    "#email-usuario",
);

const perfilDetalhe = document.querySelector(
    "#perfil-detalhe",
);

const menuUsuarios = document.querySelector(
    "#menu-usuarios",
);

const botaoSair = document.querySelector(
    "#botao-sair",
);

const alertaDashboard = document.querySelector(
    "#alerta-dashboard",
);


function redirecionarParaLogin() {
    window.location.href = LOGIN_URL;
}


function mostrarErro(mensagem) {
    alertaDashboard.textContent = mensagem;
    alertaDashboard.hidden = false;
}


function preencherUsuario(usuario) {
    nomeUsuario.textContent =
        usuario.nome ?? "Usuário";

    perfilUsuario.textContent =
        usuario.perfil ?? "SEM PERFIL";

    idUsuario.textContent =
        usuario.id ?? "—";

    emailUsuario.textContent =
        usuario.email ?? "—";

    perfilDetalhe.textContent =
        usuario.perfil ?? "—";

    if (
        usuario.perfil === "ADMINISTRADOR"
    ) {
        menuUsuarios.hidden = false;
    }
}


async function inicializarDashboard() {
    if (!obterToken()) {
        redirecionarParaLogin();
        return;
    }

    try {
        const usuario = await apiFetch(
            "/auth/me",
        );

        salvarUsuario(usuario);
        preencherUsuario(usuario);
    } catch (erro) {
        mostrarErro(
            erro.message ??
                "Não foi possível carregar o usuário.",
        );
    }
}


botaoSair.addEventListener(
    "click",
    () => {
        encerrarSessao();
        redirecionarParaLogin();
    },
);


inicializarDashboard();