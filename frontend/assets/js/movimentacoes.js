import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import { obterUsuario } from "./session.js";
import {
    definirCarregamento,
    esconderAlerta,
    escaparHtml,
    formatarData,
    mostrarAlerta,
    normalizarLista,
    valorOuNulo,
} from "./ui.js";

const formulario = document.querySelector("#form-movimentacao");
const campoTipo = document.querySelector("#movimentacao-tipo");
const campoBarril = document.querySelector("#movimentacao-barril");
const campoCliente = document.querySelector("#movimentacao-cliente");
const botaoSalvar = document.querySelector("#botao-salvar-movimentacao");
const botaoAtualizar = document.querySelector("#botao-atualizar-movimentacoes");
const alerta = document.querySelector("#alerta-movimentacao");
const tabela = document.querySelector("#tabela-movimentacoes");

let barris = [];
let clientes = [];
let movimentacoes = [];

function nomeCliente(cliente) {
    return cliente?.nome_fantasia || cliente?.nome_razao_social || `Cliente #${cliente?.id ?? "—"}`;
}

function preencherClientes() {
    const valorAtual = campoCliente.value;
    const ativos = clientes.filter((cliente) => cliente.ativo !== false);

    campoCliente.innerHTML = [
        `<option value="">Selecione o cliente</option>`,
        ...ativos.map((cliente) => `<option value="${escaparHtml(cliente.id)}">${escaparHtml(nomeCliente(cliente))}</option>`),
    ].join("");

    if (ativos.some((cliente) => String(cliente.id) === valorAtual)) {
        campoCliente.value = valorAtual;
    }
}

function preencherBarris() {
    const tipo = campoTipo.value;
    const valorAtual = campoBarril.value;
    const statusNecessario = tipo === "SAIDA_CLIENTE" ? "DISPONIVEL" : "COM_CLIENTE";
    const filtrados = barris.filter((barril) => barril.status === statusNecessario);

    campoBarril.innerHTML = [
        `<option value="">Selecione o barril</option>`,
        ...filtrados.map((barril) => `
            <option value="${escaparHtml(barril.id)}">
                ${escaparHtml(barril.codigo)} — ${escaparHtml(barril.capacidade_litros)} L
            </option>
        `),
    ].join("");

    if (filtrados.some((barril) => String(barril.id) === valorAtual)) {
        campoBarril.value = valorAtual;
    }

    atualizarClientePeloBarril();
}

function atualizarClientePeloBarril() {
    if (campoTipo.value !== "RETORNO_CLIENTE") {
        campoCliente.disabled = false;
        return;
    }

    const barril = barris.find((item) => String(item.id) === campoBarril.value);

    if (barril?.cliente_atual_id) {
        campoCliente.value = String(barril.cliente_atual_id);
        campoCliente.disabled = true;
        return;
    }

    campoCliente.disabled = false;
}

function renderizarHistorico() {
    if (!movimentacoes.length) {
        tabela.innerHTML = `<tr><td colspan="8" class="table-empty">Nenhuma movimentação encontrada.</td></tr>`;
        return;
    }

    const barrisPorId = new Map(barris.map((barril) => [barril.id, barril]));
    const clientesPorId = new Map(clientes.map((cliente) => [cliente.id, cliente]));

    tabela.innerHTML = movimentacoes.map((movimentacao) => {
        const saida = movimentacao.tipo === "SAIDA_CLIENTE";
        const barril = barrisPorId.get(movimentacao.barril_id);
        const cliente = clientesPorId.get(movimentacao.cliente_id);

        return `
            <tr>
                <td>${escaparHtml(movimentacao.id)}</td>
                <td>${escaparHtml(formatarData(movimentacao.data_movimentacao, true))}</td>
                <td>
                    <span class="status-badge ${saida ? "status-exit" : "status-return"}">
                        <i class="bi ${saida ? "bi-box-arrow-right" : "bi-box-arrow-in-left"}"></i>
                        ${saida ? "Saída" : "Retorno"}
                    </span>
                </td>
                <td><strong>${escaparHtml(barril?.codigo ?? `#${movimentacao.barril_id}`)}</strong></td>
                <td>${escaparHtml(cliente ? nomeCliente(cliente) : `#${movimentacao.cliente_id ?? "—"}`)}</td>
                <td>Usuário #${escaparHtml(movimentacao.usuario_id)}</td>
                <td>${escaparHtml(formatarData(movimentacao.data_prevista_retorno))}</td>
                <td>${escaparHtml(movimentacao.observacao || "—")}</td>
            </tr>
        `;
    }).join("");
}

async function carregarDados() {
    tabela.innerHTML = `<tr><td colspan="8" class="table-empty">Carregando histórico...</td></tr>`;

    try {
        const [respostaBarris, respostaClientes, respostaMovimentacoes] = await Promise.all([
            apiFetch(`${API_ROUTES.barris}?limite=100`),
            apiFetch(`${API_ROUTES.clientes}?limite=100`),
            apiFetch(`${API_ROUTES.movimentacoes}?limite=100`),
        ]);

        barris = normalizarLista(respostaBarris);
        clientes = normalizarLista(respostaClientes);
        movimentacoes = normalizarLista(respostaMovimentacoes);

        preencherClientes();
        preencherBarris();
        renderizarHistorico();
    } catch (erro) {
        tabela.innerHTML = `<tr><td colspan="8" class="table-empty">${escaparHtml(erro.message)}</td></tr>`;
    }
}

function montarPayload() {
    const usuario = obterUsuario();

    return {
        barril_id: Number(campoBarril.value),
        cliente_id: Number(campoCliente.value),
        usuario_id: Number(usuario?.id),
        tipo: campoTipo.value,
        data_prevista_retorno: valorOuNulo(document.querySelector("#movimentacao-previsao").value),
        responsavel_recebimento: valorOuNulo(document.querySelector("#movimentacao-responsavel").value),
        observacao: valorOuNulo(document.querySelector("#movimentacao-observacao").value),
    };
}

formulario.addEventListener("submit", async (event) => {
    event.preventDefault();
    esconderAlerta(alerta);

    if (!formulario.checkValidity() || !campoBarril.value || !campoCliente.value) {
        formulario.classList.add("was-validated");
        mostrarAlerta(alerta, "Selecione o tipo, o barril e o cliente.");
        return;
    }

    const usuario = obterUsuario();

    if (!usuario?.id) {
        mostrarAlerta(alerta, "Não foi possível identificar o usuário responsável.");
        return;
    }

    campoCliente.disabled = false;
    definirCarregamento(botaoSalvar, true, `<i class="bi bi-check2-circle me-1"></i> Confirmar movimentação`, "Registrando...");

    try {
        await apiFetch(API_ROUTES.movimentacoes, {
            method: "POST",
            body: JSON.stringify(montarPayload()),
        });

        formulario.reset();
        formulario.classList.remove("was-validated");
        campoTipo.value = "SAIDA_CLIENTE";
        mostrarAlerta(alerta, "Movimentação registrada com sucesso.", "success");
        await carregarDados();
    } catch (erro) {
        mostrarAlerta(alerta, erro.message ?? "Não foi possível registrar a movimentação.");
    } finally {
        definirCarregamento(botaoSalvar, false, `<i class="bi bi-check2-circle me-1"></i> Confirmar movimentação`);
        atualizarClientePeloBarril();
    }
});

campoTipo.addEventListener("change", preencherBarris);
campoBarril.addEventListener("change", atualizarClientePeloBarril);
botaoAtualizar.addEventListener("click", carregarDados);

carregarDados();