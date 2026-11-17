// Funções compartilhadas pelas páginas da área do cliente.

const API_URL = "http://127.0.0.1:8000/api";
const CHAVE_TOKEN = "clienteToken";

function lerToken() {
    try {
        return localStorage.getItem(CHAVE_TOKEN);
    } catch (erro) {
        return null;
    }
}

function guardarToken(token) {
    try {
        localStorage.setItem(CHAVE_TOKEN, token);
    } catch (erro) {
        // sem armazenamento: o cliente terá de entrar de novo na próxima página
    }
}

function apagarToken() {
    try {
        localStorage.removeItem(CHAVE_TOKEN);
    } catch (erro) {
        // nada a fazer
    }
}

/**
 * Chama a API e sempre devolve { ok, status, dados }, sem estourar erro.
 * Com autenticado: true, envia o token do cliente; se o servidor disser que
 * o login não vale mais (401), apaga o token e manda para a página de entrar.
 */
async function chamarApi(caminho, opcoes = {}) {
    const { metodo = "GET", corpo = null, autenticado = false } = opcoes;

    const cabecalhos = {};

    if (corpo !== null) {
        cabecalhos["Content-Type"] = "application/json";
    }

    if (autenticado) {
        const token = lerToken();

        if (token) {
            cabecalhos["Authorization"] = `Token ${token}`;
        }
    }

    let resposta;

    try {
        resposta = await fetch(`${API_URL}${caminho}`, {
            method: metodo,
            headers: cabecalhos,
            body: corpo !== null ? JSON.stringify(corpo) : undefined
        });
    } catch (erro) {
        console.error(erro);
        return {
            ok: false,
            status: 0,
            dados: { erro: "Erro de conexão com o servidor. Tente novamente." }
        };
    }

    let dados = {};

    try {
        dados = await resposta.json();
    } catch (erro) {
        dados = {};
    }

    if (resposta.status === 429) {
        dados = {
            erro: "Muitas tentativas. Aguarde um pouco e tente de novo."
        };
    }

    if (autenticado && resposta.status === 401) {
        apagarToken();
        window.location.href = "entrar.html";
    }

    return { ok: resposta.ok, status: resposta.status, dados: dados };
}

// textContent (e não innerHTML) em tudo que vem do servidor: evita XSS.
function mostrarMensagem(elemento, texto, tipo) {
    elemento.textContent = texto;
    elemento.className = tipo ? `msg msg-${tipo}` : "msg";
}

function criar(tag, texto, classe) {
    const elemento = document.createElement(tag);

    if (texto !== undefined && texto !== null) {
        elemento.textContent = texto;
    }

    if (classe) {
        elemento.className = classe;
    }

    return elemento;
}

function formatarData(dataIso) {
    const [ano, mes, dia] = dataIso.split("-");
    return `${dia}/${mes}/${ano}`;
}

function formatarHora(hora) {
    return hora.substring(0, 5);
}

function formatarReais(valor) {
    return Number(valor).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}

function dataDeHoje() {
    // AAAA-MM-DD no fuso do navegador
    return new Date().toLocaleDateString("en-CA");
}