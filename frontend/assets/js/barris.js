import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import { obterUsuario } from "./session.js";
import {
    definirCarregamento,
    esconderAlerta,
    escaparHtml,
    fecharModal,
    formatarData,
    mostrarAlerta,
    normalizarLista,
    valorOuNulo,
} from "./ui.js";

const tabela = document.querySelector("#tabela-barris");
const busca = document.querySelector("#busca-barril");
const filtroStatus = document.querySelector("#filtro-status-barril");
const botaoAtualizar = document.querySelector("#botao-atualizar-barris");
const formulario = document.querySelector("#form-barril");
const modalElemento = document.querySelector("#modal-barril");
const botaoSalvar = document.querySelector("#botao-salvar-barril");
const alerta = document.querySelector("#alerta-barril");

const totalElemento = document.querySelector("#barris-total");
const disponiveisElemento = document.querySelector("#barris-disponiveis");
const comClientesElemento = document.querySelector("#barris-com-clientes");
const litrosElemento = document.querySelector("#barris-litros");

let barris = [];
let clientesPorId = new Map();

function statusLegivel(status) {
    return status === "COM_CLIENTE" ? "Com cliente" : "Disponível";
}

function renderizarMetricas() {
    const disponiveis = barris.filter((barril) => barril.status === "DISPONIVEL").length;
    const comClientes = barris.filter((barril) => barril.status === "COM_CLIENTE").length;
    const litros = barris.reduce((total, barril) => total + Number(barril.capacidade_litros || 0), 0);

    totalElemento.textContent = String(barris.length);
    disponiveisElemento.textContent = String(disponiveis);
    comClientesElemento.textContent = String(comClientes);
    litrosElemento.textContent = litros.toLocaleString("pt-BR");
}

function renderizarTabela() {
    const termo = busca.value.trim().toLowerCase();
    const filtrados = barris.filter((barril) => {
        return !termo || String(barril.codigo ?? "").toLowerCase().includes(termo);
    });

    if (!filtrados.length) {
        tabela.innerHTML = `<tr><td colspan="7" class="table-empty">Nenhum barril encontrado.</td></tr>`;
        return;
    }

    tabela.innerHTML = filtrados.map((barril) => {
        const cliente = clientesPorId.get(barril.cliente_atual_id);
        const clienteNome = cliente?.nome_fantasia || cliente?.nome_razao_social || (barril.cliente_atual_id ? `Cliente #${barril.cliente_atual_id}` : "—");
        const comCliente = barril.status === "COM_CLIENTE";

        return `
            <tr>
                <td>${escaparHtml(barril.id)}</td>
                <td><strong class="text-burgundy">${escaparHtml(barril.codigo)}</strong></td>
                <td>${escaparHtml(barril.capacidade_litros)} L</td>
                <td>
                    <span class="status-badge ${comCliente ? "status-client" : "status-available"}">
                        <i class="bi ${comCliente ? "bi-truck" : "bi-check-circle"}"></i>
                        ${statusLegivel(barril.status)}
                    </span>
                </td>
                <td>${escaparHtml(clienteNome)}</td>
                <td>${escaparHtml(formatarData(barril.data_aquisicao))}</td>
                <td>${escaparHtml(barril.observacao || "—")}</td>
            </tr>
        `;
    }).join("");
}

async function carregarDados() {
    tabela.innerHTML = `<tr><td colspan="7" class="table-empty">Carregando barris...</td></tr>`;

    const parametroStatus = filtroStatus.value
        ? `&status=${encodeURIComponent(filtroStatus.value)}`
        : "";

    try {
        const [respostaBarris, respostaClientes] = await Promise.all([
            apiFetch(`${API_ROUTES.barris}?limite=100${parametroStatus}`),
            apiFetch(`${API_ROUTES.clientes}?limite=100`),
        ]);

        barris = normalizarLista(respostaBarris);
        clientesPorId = new Map(normalizarLista(respostaClientes).map((cliente) => [cliente.id, cliente]));
        renderizarMetricas();
        renderizarTabela();
    } catch (erro) {
        tabela.innerHTML = `<tr><td colspan="7" class="table-empty">${escaparHtml(erro.message)}</td></tr>`;
    }
}

function montarPayload() {
    return {
        codigo: document.querySelector("#barril-codigo").value.trim().toUpperCase(),
        capacidade_litros: Number(document.querySelector("#barril-capacidade").value),
        data_aquisicao: valorOuNulo(document.querySelector("#barril-data-aquisicao").value),
        observacao: valorOuNulo(document.querySelector("#barril-observacao").value),
    };
}

formulario.addEventListener("submit", async (event) => {
    event.preventDefault();
    esconderAlerta(alerta);

    if (!formulario.checkValidity()) {
        formulario.classList.add("was-validated");
        mostrarAlerta(alerta, "Preencha o código e a capacidade do barril.");
        return;
    }

    const usuario = obterUsuario();

    if (!usuario?.id) {
        mostrarAlerta(alerta, "Não foi possível identificar o usuário responsável pela inclusão.");
        return;
    }

    definirCarregamento(botaoSalvar, true, "Salvar barril");

    try {
        await apiFetch(`${API_ROUTES.barris}?usuario_id=${encodeURIComponent(usuario.id)}`, {
            method: "POST",
            body: JSON.stringify(montarPayload()),
        });

        formulario.reset();
        formulario.classList.remove("was-validated");
        document.querySelector("#barril-capacidade").value = "50";
        fecharModal(modalElemento);
        await carregarDados();
    } catch (erro) {
        mostrarAlerta(alerta, erro.message ?? "Não foi possível cadastrar o barril.");
    } finally {
        definirCarregamento(botaoSalvar, false, "Salvar barril");
    }
});

busca.addEventListener("input", renderizarTabela);
filtroStatus.addEventListener("change", carregarDados);
botaoAtualizar.addEventListener("click", carregarDados);

modalElemento.addEventListener("hidden.bs.modal", () => {
    esconderAlerta(alerta);
    formulario.classList.remove("was-validated");
});

if (window.location.hash === "#novo") {
    bootstrap.Modal.getOrCreateInstance(modalElemento).show();
}

carregarDados();