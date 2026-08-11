export function mostrarAlerta(elemento, mensagem, tipo = "danger") {
    if (!elemento) {
        return;
    }

    elemento.className = `alert alert-${tipo}`;
    elemento.textContent = mensagem;
    elemento.hidden = false;
}

export function esconderAlerta(elemento) {
    if (!elemento) {
        return;
    }

    elemento.hidden = true;
    elemento.textContent = "";
}

export function definirCarregamento(botao, carregando, textoNormal, textoCarregando = "Salvando...") {
    if (!botao) {
        return;
    }

    botao.disabled = carregando;
    botao.innerHTML = carregando
        ? `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>${textoCarregando}`
        : textoNormal;
}

export function valorOuNulo(valor) {
    if (typeof valor !== "string") {
        return valor ?? null;
    }

    const limpo = valor.trim();
    return limpo || null;
}

export function somenteDigitos(valor) {
    return String(valor ?? "").replace(/\D/g, "");
}

export function formatarData(valor, incluirHora = false) {
    if (!valor) {
        return "—";
    }

    const texto = String(valor);
    const dataSomente = /^\d{4}-\d{2}-\d{2}$/.test(texto);
    const data = dataSomente
        ? new Date(
            Number(texto.slice(0, 4)),
            Number(texto.slice(5, 7)) - 1,
            Number(texto.slice(8, 10)),
        )
        : new Date(texto);

    if (Number.isNaN(data.getTime())) {
        return texto;
    }

    return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        ...(!dataSomente && incluirHora ? { timeStyle: "short" } : {}),
    }).format(data);
}

export function formatarDocumento(valor) {
    const digitos = somenteDigitos(valor);

    if (digitos.length === 11) {
        return digitos.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
    }

    if (digitos.length === 14) {
        return digitos.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
    }

    return valor || "—";
}

export function escaparHtml(valor) {
    return String(valor ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

export function normalizarLista(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data?.items)) {
        return data.items;
    }

    if (Array.isArray(data?.results)) {
        return data.results;
    }

    return [];
}

export function fecharModal(elementoModal) {
    if (!elementoModal || typeof bootstrap === "undefined") {
        return;
    }

    bootstrap.Modal.getOrCreateInstance(elementoModal).hide();
}