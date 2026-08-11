import { apiFetch } from "./api.js";
import { API_ROUTES } from "./config.js";
import {
    escaparHtml,
    formatarData,
    normalizarLista,
} from "./ui.js";

const metricClientes = document.querySelector("#metric-clientes");
const metricDisponiveis = document.querySelector("#metric-disponiveis");
const metricComClientes = document.querySelector("#metric-com-clientes");
const metricMovimentacoes = document.querySelector("#metric-movimentacoes");
const tabelaMovimentacoes = document.querySelector("#tabela-movimentacoes-recentes");
const percentualDisponiveis = document.querySelector("#percentual-disponiveis");
const percentualComClientes = document.querySelector("#percentual-com-clientes");
const barraDisponiveis = document.querySelector("#barra-disponiveis");
const barraComClientes = document.querySelector("#barra-com-clientes");

function obterNomeCliente(cliente) {
    return cliente?.nome_fantasia || cliente?.nome_razao_social || `Cliente #${cliente?.id ?? "—"}`;
}

function renderizarMovimentacoes(movimentacoes, barris, clientes) {
    if (!movimentacoes.length) {
        tabelaMovimentacoes.innerHTML = `
            <tr>
                <td colspan="5" class="table-empty">Nenhuma movimentação encontrada.</td>
            </tr>
        `;
        return;
    }

    const barrisPorId = new Map(barris.map((barril) => [barril.id, barril]));
    const clientesPorId = new Map(clientes.map((cliente) => [cliente.id, cliente]));

    tabelaMovimentacoes.innerHTML = movimentacoes.slice(0, 8).map((movimentacao) => {
        const barril = barrisPorId.get(movimentacao.barril_id);
        const cliente = clientesPorId.get(movimentacao.cliente_id);
        const tipoSaida = movimentacao.tipo === "SAIDA_CLIENTE";

        return `
            <tr>
                <td>${escaparHtml(formatarData(movimentacao.data_movimentacao, true))}</td>
                <td>
                    <span class="status-badge ${tipoSaida ? "status-exit" : "status-return"}">
                        <i class="bi ${tipoSaida ? "bi-box-arrow-right" : "bi-box-arrow-in-left"}"></i>
                        ${tipoSaida ? "Saída" : "Retorno"}
                    </span>
                </td>
                <td><strong>${escaparHtml(barril?.codigo ?? `#${movimentacao.barril_id}`)}</strong></td>
                <td>${escaparHtml(cliente ? obterNomeCliente(cliente) : `#${movimentacao.cliente_id ?? "—"}`)}</td>
                <td>Usuário #${escaparHtml(movimentacao.usuario_id ?? "—")}</td>
            </tr>
        `;
    }).join("");
}

function atualizarSituacaoEstoque(disponiveis, comClientes) {
    const total = disponiveis + comClientes;
    const percentualDisponivel = total ? Math.round((disponiveis / total) * 100) : 0;
    const percentualCliente = total ? 100 - percentualDisponivel : 0;

    percentualDisponiveis.textContent = `${percentualDisponivel}%`;
    percentualComClientes.textContent = `${percentualCliente}%`;
    barraDisponiveis.style.width = `${percentualDisponivel}%`;
    barraComClientes.style.width = `${percentualCliente}%`;
}

async function carregarDashboard() {
    const resultados = await Promise.allSettled([
        apiFetch(`${API_ROUTES.clientes}?limite=100&ativo=true`),
        apiFetch(`${API_ROUTES.barris}?limite=100`),
        apiFetch(`${API_ROUTES.movimentacoes}?limite=100`),
    ]);

    const clientes = resultados[0].status === "fulfilled"
        ? normalizarLista(resultados[0].value)
        : [];
    const barris = resultados[1].status === "fulfilled"
        ? normalizarLista(resultados[1].value)
        : [];
    const movimentacoes = resultados[2].status === "fulfilled"
        ? normalizarLista(resultados[2].value)
        : [];

    const disponiveis = barris.filter((barril) => barril.status === "DISPONIVEL").length;
    const comClientes = barris.filter((barril) => barril.status === "COM_CLIENTE").length;

    metricClientes.textContent = resultados[0].status === "fulfilled" ? clientes.length : "—";
    metricDisponiveis.textContent = resultados[1].status === "fulfilled" ? disponiveis : "—";
    metricComClientes.textContent = resultados[1].status === "fulfilled" ? comClientes : "—";
    metricMovimentacoes.textContent = resultados[2].status === "fulfilled" ? movimentacoes.length : "—";

    atualizarSituacaoEstoque(disponiveis, comClientes);
    renderizarMovimentacoes(movimentacoes, barris, clientes);
}

carregarDashboard().catch(() => {
    tabelaMovimentacoes.innerHTML = `
        <tr>
            <td colspan="5" class="table-empty">Não foi possível carregar os dados do painel.</td>
        </tr>
    `;
});