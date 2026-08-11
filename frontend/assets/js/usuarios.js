import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import {
    definirCarregamento,
    esconderAlerta,
    escaparHtml,
    fecharModal,
    formatarData,
    mostrarAlerta,
    normalizarLista,
} from "./ui.js";

const tabela = document.querySelector("#tabela-usuarios");
const botaoAtualizar = document.querySelector("#botao-atualizar-usuarios");
const formulario = document.querySelector("#form-usuario");
const botaoSalvar = document.querySelector("#botao-salvar-usuario");
const alerta = document.querySelector("#alerta-usuario");
const modalElemento = document.querySelector("#modal-usuario");

function perfilLegivel(perfil) {
    return perfil === "ADMINISTRADOR" ? "Administrador" : "Operador";
}

function renderizar(usuarios) {
    if (!usuarios.length) {
        tabela.innerHTML = `<tr><td colspan="6" class="table-empty">Nenhum usuário encontrado.</td></tr>`;
        return;
    }

    tabela.innerHTML = usuarios.map((usuario) => `
        <tr>
            <td>${escaparHtml(usuario.id)}</td>
            <td><strong>${escaparHtml(usuario.nome)}</strong></td>
            <td>${escaparHtml(usuario.email)}</td>
            <td><span class="user-badge">${escaparHtml(perfilLegivel(usuario.perfil))}</span></td>
            <td>
                <span class="status-badge ${usuario.ativo ? "status-active" : "status-inactive"}">
                    <i class="bi ${usuario.ativo ? "bi-check-circle" : "bi-dash-circle"}"></i>
                    ${usuario.ativo ? "Ativo" : "Inativo"}
                </span>
            </td>
            <td>${escaparHtml(formatarData(usuario.criado_em, true))}</td>
        </tr>
    `).join("");
}

async function carregarUsuarios() {
    tabela.innerHTML = `<tr><td colspan="6" class="table-empty">Carregando usuários...</td></tr>`;

    try {
        const resposta = await apiFetch(`${API_ROUTES.usuarios}?limite=100`);
        renderizar(normalizarLista(resposta));
    } catch (erro) {
        tabela.innerHTML = `<tr><td colspan="6" class="table-empty">${escaparHtml(erro.message)}</td></tr>`;
    }
}

formulario.addEventListener("submit", async (event) => {
    event.preventDefault();
    esconderAlerta(alerta);

    if (!formulario.checkValidity()) {
        formulario.classList.add("was-validated");
        mostrarAlerta(alerta, "Preencha nome, e-mail, senha e perfil.");
        return;
    }

    const payload = {
        nome: document.querySelector("#usuario-nome").value.trim(),
        email: document.querySelector("#usuario-email").value.trim().toLowerCase(),
        senha: document.querySelector("#usuario-senha").value,
        perfil: document.querySelector("#usuario-perfil").value,
        ativo: true,
    };

    definirCarregamento(botaoSalvar, true, "Salvar usuário");

    try {
        await apiFetch(API_ROUTES.usuarios, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        formulario.reset();
        formulario.classList.remove("was-validated");
        document.querySelector("#usuario-perfil").value = "OPERADOR";
        fecharModal(modalElemento);
        await carregarUsuarios();
    } catch (erro) {
        mostrarAlerta(alerta, erro.message ?? "Não foi possível cadastrar o usuário.");
    } finally {
        definirCarregamento(botaoSalvar, false, "Salvar usuário");
    }
});

botaoAtualizar.addEventListener("click", carregarUsuarios);
modalElemento.addEventListener("hidden.bs.modal", () => {
    esconderAlerta(alerta);
    formulario.classList.remove("was-validated");
});

carregarUsuarios();