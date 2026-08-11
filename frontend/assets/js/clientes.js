import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import {
    definirCarregamento,
    esconderAlerta,
    escaparHtml,
    fecharModal,
    formatarDocumento,
    mostrarAlerta,
    normalizarLista,
    somenteDigitos,
    valorOuNulo,
} from "./ui.js";

const tabela = document.querySelector("#tabela-clientes");
const busca = document.querySelector("#busca-cliente");
const filtroAtivo = document.querySelector("#filtro-cliente-ativo");
const botaoAtualizar = document.querySelector("#botao-atualizar-clientes");
const modalElemento = document.querySelector("#modal-cliente");
const formulario = document.querySelector("#form-cliente");
const botaoSalvar = document.querySelector("#botao-salvar-cliente");
const alerta = document.querySelector("#alerta-cliente");

let clientes = [];

function obterNome(cliente) {
    return cliente.nome_fantasia || cliente.nome_razao_social || "Cliente sem nome";
}

function tipoPessoaLegivel(tipo) {
    const normalizado = String(tipo ?? "").toUpperCase();
    return normalizado.includes("JURIDICA") ? "Pessoa jurídica" : "Pessoa física";
}

function renderizar() {
    const termo = busca.value.trim().toLowerCase();

    const filtrados = clientes.filter((cliente) => {
        const texto = [
            cliente.nome_razao_social,
            cliente.nome_fantasia,
            cliente.documento,
            cliente.cidade,
        ].join(" ").toLowerCase();

        return !termo || texto.includes(termo);
    });

    if (!filtrados.length) {
        tabela.innerHTML = `<tr><td colspan="7" class="table-empty">Nenhum cliente encontrado.</td></tr>`;
        return;
    }

    tabela.innerHTML = filtrados.map((cliente) => `
        <tr>
            <td>${escaparHtml(cliente.id)}</td>
            <td>
                <strong>${escaparHtml(obterNome(cliente))}</strong>
                ${cliente.nome_fantasia && cliente.nome_razao_social
                    ? `<div class="small text-secondary">${escaparHtml(cliente.nome_razao_social)}</div>`
                    : ""}
            </td>
            <td>${escaparHtml(tipoPessoaLegivel(cliente.tipo_pessoa))}</td>
            <td>${escaparHtml(formatarDocumento(cliente.documento))}</td>
            <td>
                <div>${escaparHtml(cliente.telefone || "—")}</div>
                <small class="text-secondary">${escaparHtml(cliente.email || "")}</small>
            </td>
            <td>${escaparHtml([cliente.cidade, cliente.estado].filter(Boolean).join("/") || "—")}</td>
            <td>
                <span class="status-badge ${cliente.ativo ? "status-active" : "status-inactive"}">
                    <i class="bi ${cliente.ativo ? "bi-check-circle" : "bi-dash-circle"}"></i>
                    ${cliente.ativo ? "Ativo" : "Inativo"}
                </span>
            </td>
        </tr>
    `).join("");
}

async function carregarClientes() {
    tabela.innerHTML = `<tr><td colspan="7" class="table-empty">Carregando clientes...</td></tr>`;

    const parametroAtivo = filtroAtivo.value
        ? `&ativo=${encodeURIComponent(filtroAtivo.value)}`
        : "";

    try {
        const resposta = await apiFetch(`${API_ROUTES.clientes}?limite=100${parametroAtivo}`);
        clientes = normalizarLista(resposta);
        renderizar();
    } catch (erro) {
        tabela.innerHTML = `<tr><td colspan="7" class="table-empty">${escaparHtml(erro.message)}</td></tr>`;
    }
}

function montarPayload() {
    return {
        tipo_pessoa: document.querySelector("#cliente-tipo").value,
        nome_razao_social: document.querySelector("#cliente-nome").value.trim(),
        nome_fantasia: valorOuNulo(document.querySelector("#cliente-fantasia").value),
        documento: valorOuNulo(somenteDigitos(document.querySelector("#cliente-documento").value)),
        telefone: valorOuNulo(document.querySelector("#cliente-telefone").value),
        email: valorOuNulo(document.querySelector("#cliente-email").value)?.toLowerCase() ?? null,
        logradouro: valorOuNulo(document.querySelector("#cliente-logradouro").value),
        numero: valorOuNulo(document.querySelector("#cliente-numero").value),
        complemento: valorOuNulo(document.querySelector("#cliente-complemento").value),
        bairro: valorOuNulo(document.querySelector("#cliente-bairro").value),
        cidade: valorOuNulo(document.querySelector("#cliente-cidade").value),
        estado: valorOuNulo(document.querySelector("#cliente-estado").value)?.toUpperCase() ?? null,
        cep: valorOuNulo(somenteDigitos(document.querySelector("#cliente-cep").value)),
        ativo: true,
    };
}

formulario.addEventListener("submit", async (event) => {
    event.preventDefault();
    esconderAlerta(alerta);

    if (!formulario.checkValidity()) {
        formulario.classList.add("was-validated");
        mostrarAlerta(alerta, "Preencha os campos obrigatórios do cliente.");
        return;
    }

    definirCarregamento(botaoSalvar, true, "Salvar cliente");

    try {
        await apiFetch(API_ROUTES.clientes, {
            method: "POST",
            body: JSON.stringify(montarPayload()),
        });

        formulario.reset();
        formulario.classList.remove("was-validated");
        document.querySelector("#cliente-tipo").value = "JURIDICA";
        fecharModal(modalElemento);
        await carregarClientes();
    } catch (erro) {
        mostrarAlerta(alerta, erro.message ?? "Não foi possível cadastrar o cliente.");
    } finally {
        definirCarregamento(botaoSalvar, false, "Salvar cliente");
    }
});

busca.addEventListener("input", renderizar);
filtroAtivo.addEventListener("change", carregarClientes);
botaoAtualizar.addEventListener("click", carregarClientes);

modalElemento.addEventListener("hidden.bs.modal", () => {
    esconderAlerta(alerta);
    formulario.classList.remove("was-validated");
});

if (window.location.hash === "#novo") {
    bootstrap.Modal.getOrCreateInstance(modalElemento).show();
}

carregarClientes();