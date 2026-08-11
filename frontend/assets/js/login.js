import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import {
    encerrarSessao,
    obterEmailLembrado,
    possuiSessao,
    salvarEmailLembrado,
    salvarToken,
    salvarUsuario,
} from "./session.js";
import {
    esconderAlerta,
    mostrarAlerta,
} from "./ui.js";

const DASHBOARD_URL = new URL("../../pages/dashboard.html", import.meta.url).href;

const formulario = document.querySelector("#form-login");
const campoEmail = document.querySelector("#email");
const campoSenha = document.querySelector("#senha");
const lembrarEmail = document.querySelector("#lembrar-email");
const botaoEntrar = document.querySelector("#botao-entrar");
const botaoMostrarSenha = document.querySelector("#botao-mostrar-senha");
const alerta = document.querySelector("#alerta-login");

function alterarCarregamento(carregando) {
    botaoEntrar.disabled = carregando;
    botaoEntrar.innerHTML = carregando
        ? `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Entrando...`
        : `<i class="bi bi-box-arrow-in-right me-2"></i>Entrar`;
}

function configurarEmailLembrado() {
    const emailSalvo = obterEmailLembrado();

    if (!emailSalvo) {
        campoEmail.focus();
        return;
    }

    campoEmail.value = emailSalvo;
    lembrarEmail.checked = true;
    campoSenha.focus();
}

function configurarExibicaoSenha() {
    botaoMostrarSenha.addEventListener("click", () => {
        const mostrar = campoSenha.type === "password";
        campoSenha.type = mostrar ? "text" : "password";
        botaoMostrarSenha.setAttribute("aria-pressed", String(mostrar));
        botaoMostrarSenha.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
        botaoMostrarSenha.innerHTML = mostrar
            ? `<i class="bi bi-eye-slash"></i>`
            : `<i class="bi bi-eye"></i>`;
    });
}

async function verificarSessaoExistente() {
    if (!possuiSessao()) {
        return;
    }

    try {
        const usuario = await apiFetch(API_ROUTES.usuarioAtual);
        salvarUsuario(usuario);
        window.location.replace(DASHBOARD_URL);
    } catch {
        encerrarSessao();
    }
}

formulario.addEventListener("submit", async (event) => {
    event.preventDefault();
    esconderAlerta(alerta);

    const email = campoEmail.value.trim().toLowerCase();
    const senha = campoSenha.value;

    if (!formulario.checkValidity() || !email || !senha) {
        formulario.classList.add("was-validated");
        mostrarAlerta(alerta, "Informe um e-mail válido e a senha de acesso.");
        return;
    }

    alterarCarregamento(true);

    try {
        const respostaLogin = await apiFetch(API_ROUTES.login, {
            method: "POST",
            auth: false,
            body: JSON.stringify({ email, senha }),
        });

        if (!respostaLogin?.access_token) {
            throw new Error("A API não retornou o access_token.");
        }

        salvarToken(respostaLogin.access_token);

        const usuario = await apiFetch(API_ROUTES.usuarioAtual);
        salvarUsuario(usuario);
        salvarEmailLembrado(lembrarEmail.checked ? email : "");

        window.location.replace(DASHBOARD_URL);
    } catch (erro) {
        encerrarSessao();
        mostrarAlerta(
            alerta,
            erro.message ?? "Não foi possível realizar o login.",
        );
    } finally {
        alterarCarregamento(false);
    }
});

configurarEmailLembrado();
configurarExibicaoSenha();
verificarSessaoExistente();