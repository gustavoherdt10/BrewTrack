import { apiFetch } from "./api.js";
import {
    encerrarSessao,
    possuiSessao,
    salvarToken,
    salvarUsuario,
} from "./session.js";


const DASHBOARD_URL = new URL(
    "../../pages/dashboard.html",
    import.meta.url,
).href;


const formulario = document.querySelector(
    "#form-login",
);

const campoEmail = document.querySelector(
    "#email",
);

const campoSenha = document.querySelector(
    "#senha",
);

const botaoEntrar = document.querySelector(
    "#botao-entrar",
);

const alerta = document.querySelector(
    "#alerta-login",
);


function mostrarMensagem(
    mensagem,
    tipo = "danger",
) {
    alerta.className = `alert alert-${tipo}`;
    alerta.textContent = mensagem;
    alerta.hidden = false;
}


function esconderMensagem() {
    alerta.hidden = true;
    alerta.textContent = "";
}


function alterarCarregamento(carregando) {
    botaoEntrar.disabled = carregando;

    if (carregando) {
        botaoEntrar.innerHTML = `
            <span
                class="spinner-border spinner-border-sm"
                aria-hidden="true"
            ></span>
            Entrando...
        `;
        return;
    }

    botaoEntrar.textContent = "Entrar";
}


async function verificarSessaoExistente() {
    if (!possuiSessao()) {
        return;
    }

    try {
        const usuario = await apiFetch(
            "/auth/me",
        );

        salvarUsuario(usuario);

        window.location.href = DASHBOARD_URL;
    } catch {
        encerrarSessao();
    }
}


formulario.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        esconderMensagem();

        const email = campoEmail.value
            .trim()
            .toLowerCase();

        const senha = campoSenha.value;

        if (!email || !senha) {
            mostrarMensagem(
                "Informe o e-mail e a senha.",
            );
            return;
        }

        alterarCarregamento(true);

        try {
            const respostaLogin = await apiFetch(
                "/auth/login",
                {
                    method: "POST",
                    body: JSON.stringify({
                        email,
                        senha,
                    }),
                },
            );

            if (!respostaLogin.access_token) {
                throw new Error(
                    "A API não retornou o access_token.",
                );
            }

            salvarToken(
                respostaLogin.access_token,
            );

            const usuario = await apiFetch(
                "/auth/me",
            );

            salvarUsuario(usuario);

            window.location.href =
                DASHBOARD_URL;
        } catch (erro) {
            encerrarSessao();

            mostrarMensagem(
                erro.message ??
                    "Não foi possível realizar o login.",
            );
        } finally {
            alterarCarregamento(false);
        }
    },
);


verificarSessaoExistente();