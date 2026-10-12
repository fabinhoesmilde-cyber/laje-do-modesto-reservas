const API_URL = "http://127.0.0.1:8000/api";

const adminToken = localStorage.getItem("adminToken");
const adminUsername = localStorage.getItem("adminUsername");

if (!adminToken) {
    window.location.href = "admin-login.html";
}

const usuarioLogado = document.getElementById("usuarioLogado");

if (usuarioLogado) {
    usuarioLogado.textContent = `Bem-vindo, ${adminUsername}`;
}

const campoBuscaReserva = document.getElementById("campoBuscaReserva");

const listaReservas = document.getElementById("listaReservas");

const totalReservas = document.getElementById("totalReservas");
const totalConfirmadas = document.getElementById("totalConfirmadas");
const totalCanceladas = document.getElementById("totalCanceladas");
const totalAlteracoes = document.getElementById("totalAlteracoes");
const totalCancelamentos = document.getElementById("totalCancelamentos");

let todasReservas = [];
let filtroAtual = "TODAS";
let clientesEncontrados = [];

async function carregarReservas() {

    try {

        const resposta = await fetch(`${API_URL}/reservas/`);

        if (!resposta.ok) {
            throw new Error("Erro ao carregar reservas.");
        }

        todasReservas = await resposta.json();

        atualizarDashboard();

        carregarProximaReserva();

        renderizarReservas();

    } catch (erro) {

        console.error(erro);

        listaReservas.innerHTML = `

            <div class="painel-reserva">

                <h3>Erro ao carregar reservas.</h3>

            </div>

        `;

    }

}

function atualizarDashboard() {

    totalReservas.textContent =
        todasReservas.length;

    totalConfirmadas.textContent =
        todasReservas.filter(
            r => r.status_nome === "CONFIRMADA"
        ).length;

    totalCanceladas.textContent =
        todasReservas.filter(
            r => r.status_nome === "CANCELADA"
        ).length;

    totalAlteracoes.textContent =
        todasReservas.filter(
            r => r.status_nome === "ALTERACAO_SOLICITADA"
        ).length;

    totalCancelamentos.textContent =
        todasReservas.filter(
            r => r.status_nome === "CANCELAMENTO_SOLICITADO"
        ).length;

}

function criarCardReserva(reserva) {

    let classeStatus = "";
    let botoes = "";

    switch (reserva.status_nome) {

        case "CONFIRMADA":

            classeStatus = "status-confirmada";

            break;

        case "ALTERACAO_SOLICITADA":

            classeStatus = "status-alteracao";

            botoes = `

                <button onclick="aprovarAlteracao('${reserva.codigo_reserva}')">

                    ✔ Aprovar

                </button>

                <button onclick="rejeitarAlteracao('${reserva.codigo_reserva}')">

                    ✖ Rejeitar

                </button>

            `;

            break;

        case "CANCELAMENTO_SOLICITADO":

            classeStatus = "status-cancelamento";

            botoes = `

                <button onclick="aprovarCancelamento('${reserva.codigo_reserva}')">

                    ✔ Aprovar

                </button>

                <button onclick="rejeitarCancelamento('${reserva.codigo_reserva}')">

                    ✖ Rejeitar

                </button>

            `;

            break;

    }

    return `

    <div class="painel-reserva ${classeStatus}">

        <div class="cabecalho-reserva">

            <h3>

                👤 ${reserva.cliente_nome}

            </h3>

            <span class="badge-status">

                ${reserva.status_nome}

            </span>

        </div>

        <div class="info-reserva">

            <p>

                📌 <strong>Código:</strong>

                ${reserva.codigo_reserva}

            </p>

            <p>

                📅 <strong>Data:</strong>

                ${reserva.data_reserva}

            </p>

            <p>

                🕒 <strong>Horário:</strong>

                ${reserva.hora_inicio}

                às

                ${reserva.hora_fim}

            </p>

            <p>

                💰 <strong>Total:</strong>

                R$ ${reserva.valor_total}

            </p>

        </div>

        <div class="acoes-reserva">

            <button
                class="btn-ver"
                onclick="abrirReserva('${reserva.codigo_reserva}')"
            >

                👁 Ver

            </button>

            ${botoes}

        </div>

    </div>

    `;

}

function renderizarReservas() {

    listaReservas.innerHTML = "";

    let reservas = todasReservas;

    if (filtroAtual !== "TODAS") {

        reservas = reservas.filter(
            r => r.status_nome === filtroAtual
        );

    }

    reservas.forEach(reserva => {

        listaReservas.innerHTML += criarCardReserva(reserva);

    });

}

const modal = document.getElementById("modalReserva");
const botaoFecharModal = document.getElementById("fecharModal");

botaoFecharModal.onclick = function () {

    modal.style.display = "none";

}

window.onclick = function (event) {

    if (event.target === modal) {

        modal.style.display = "none";

    }

}

document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {

        modal.style.display = "none";

    }

});

function logoutAdmin() {

    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminUsername");

    window.location.href = "admin-login.html";

}

function buscarReservaPorCodigo() {

    const codigo = campoBuscaReserva.value
        .trim()
        .toLowerCase();

    if (!codigo) {

        renderizarReservas();

        return;

    }

    const cards = document.querySelectorAll(".painel-reserva");

    cards.forEach(card => {

        const texto = card.textContent.toLowerCase();

        if (texto.includes(codigo)) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });

}

function limparBuscaReserva() {

    campoBuscaReserva.value = "";

    renderizarReservas();

}
/* ===========================
   FILTROS
=========================== */

const botoesFiltro =
    document.querySelectorAll(".filtro");

botoesFiltro.forEach(botao => {

    botao.addEventListener("click", () => {

        botoesFiltro.forEach(btn =>
            btn.classList.remove("ativo")
        );

        botao.classList.add("ativo");

        filtroAtual =
            botao.dataset.status;

        renderizarReservas();

    });

});


/* ===========================
   DASHBOARD
=========================== */

const cardsDashboard =
    document.querySelectorAll(".dashboard-card");

cardsDashboard.forEach(card => {

    card.addEventListener("click", () => {

        filtroAtual =
            card.dataset.status;

        botoesFiltro.forEach(btn =>
            btn.classList.remove("ativo")
        );

        const filtro =
            document.querySelector(
                `.filtro[data-status="${filtroAtual}"]`
            );

        if (filtro) {

            filtro.classList.add("ativo");

        }

        renderizarReservas();

        listaReservas.scrollIntoView({

            behavior: "smooth"

        });

    });

});


/* ===========================
   BUSCA COM ENTER
=========================== */

campoBuscaReserva.addEventListener("keypress", (e) => {

    if (e.key === "Enter") {

        buscarReservaPorCodigo();

    }

});
/* ===========================
   INICIALIZAÇÃO
=========================== */

document.addEventListener("DOMContentLoaded", () => {

    carregarReservas();

});

/* ===========================
   Area de pesquisa do cliente
=========================== */

async function abrirModalClientes() {

    const modal = document.getElementById("modalClientes");
    const resultado = document.getElementById("resultadoClientes");
    const campo = document.getElementById("campoBuscaCliente");

    if (!modal || !resultado) {
        return;
    }

    modal.style.display = "flex";

    if (campo) {
        campo.value = "";
    }

    resultado.innerHTML = `
        <p class="mensagem-clientes">
            Carregando clientes...
        </p>
    `;

    try {

        const resposta = await fetch(
            `${API_URL}/clientes/`
        );

        if (!resposta.ok) {
            throw new Error("Erro ao carregar clientes.");
        }

        clientesEncontrados = await resposta.json();

        mostrarClientes(clientesEncontrados);

    } catch (erro) {

        console.error(erro);

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Não foi possível carregar os clientes.
            </p>
        `;

    }

}

function mostrarClientes(clientes) {

    const resultado = document.getElementById("resultadoClientes");

    if (!resultado) {
        return;
    }

    if (clientes.length === 0) {

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Nenhum cliente cadastrado.
            </p>
        `;

        return;

    }

    resultado.innerHTML = clientes.map(cliente => `

        <div class="cliente-resultado">

            <div>

                <strong>
                    ${cliente.nome}
                </strong>

                <p>
                    CPF: ${cliente.cpf}
                </p>

                <p>
                    Telefone: ${cliente.telefone}
                </p>

                <p>
                    E-mail: ${cliente.email}
                </p>

            </div>

            <button
                class="btn-ver-cliente"
                onclick="verCliente(${cliente.id})"
            >
                <i class="fa-solid fa-eye"></i>
                Ver cliente
            </button>

        </div>

    `).join("");

}

function fecharModalClientes() {

    const modal = document.getElementById("modalClientes");

    if (modal) {
        modal.style.display = "none";
    }

}

async function buscarClientes() {


    const campo = document.getElementById("campoBuscaCliente");
    const resultado = document.getElementById("resultadoClientes");

    const busca = campo.value.trim().toLowerCase();

    if (!busca) {

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Digite o nome, CPF ou telefone do cliente.
            </p>
        `;

        return;
    }

    try {

        const resposta = await fetch(
            "http://127.0.0.1:8000/api/clientes/"
        );

        if (!resposta.ok) {
            throw new Error("Erro ao buscar clientes.");
        }

        const clientes = await resposta.json();

        clientesEncontrados = clientes.filter(cliente => {

            return (
                cliente.nome.toLowerCase().includes(busca) ||
                cliente.cpf.includes(busca) ||
                cliente.telefone.includes(busca)
            );

        });

        if (clientesEncontrados.length === 0) {

            resultado.innerHTML = `
                <p class="mensagem-clientes">
                    Nenhum cliente encontrado.
                </p>
            `;

            return;
        }

resultado.innerHTML = clientesEncontrados.map(cliente => `

    <div class="cliente-resultado">

        <div>

            <strong>
                ${cliente.nome}
            </strong>

            <p>
                CPF: ${cliente.cpf}
            </p>

            <p>
                Telefone: ${cliente.telefone}
            </p>

            <p>
                E-mail: ${cliente.email}
            </p>

        </div>

        <button
            class="btn-ver-cliente"
            onclick="verCliente(${cliente.id})"
        >
            <i class="fa-solid fa-eye"></i>
            Ver cliente
        </button>

    </div>

`).join("");

    } catch (erro) {

        console.error(erro);

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Não foi possível carregar os clientes.
            </p>
        `;

    }

}

function verCliente(id) {

    const cliente = clientesEncontrados.find(
        cliente => cliente.id === id
    );

    if (!cliente) {
        alert("Cliente não encontrado.");
        return;
    }

    const resultado = document.getElementById("resultadoClientes");

    resultado.innerHTML = `

        <div class="detalhes-cliente">

            <div class="cabecalho-cliente">

                <div>

                    <span class="modal-subtitulo">
                        Cliente selecionado
                    </span>

                    <h2>
                        👤 ${cliente.nome}
                    </h2>

                </div>

            </div>

            <div class="grid-modal">

                <div class="info-box">

                    <h3>
                        👤 Informações pessoais
                    </h3>

                    <p>
                        <strong>Nome</strong>
                        ${cliente.nome}
                    </p>

                    <p>
                        <strong>CPF</strong>
                        ${cliente.cpf}
                    </p>

                </div>

                <div class="info-box">

                    <h3>
                        📞 Contato
                    </h3>

                    <p>
                        <strong>Telefone</strong>
                        ${cliente.telefone}
                    </p>

                    <p>
                        <strong>E-mail</strong>
                        ${cliente.email}
                    </p>

                </div>

                <div class="info-box info-box-full">

                    <h3>
                        📅 Cadastro
                    </h3>

                    <p>
                        <strong>Cadastrado em</strong>
                        ${new Date(cliente.criado_em).toLocaleDateString("pt-BR")}
                    </p>

                </div>

            </div>

            <div class="acoes-cliente">

                <button
                    class="btn-voltar-cliente"
                    onclick="voltarBuscaClientes()"
                >
                    <i class="fa-solid fa-arrow-left"></i>
                    Voltar
                </button>

                <button
                    class="btn-editar-cliente"
                    onclick="editarCliente(${cliente.id})"
                >
                    <i class="fa-solid fa-pen"></i>
                    Editar cliente
                </button>

            </div>

        </div>

    `;

}
function voltarBuscaClientes() {

    const resultado = document.getElementById("resultadoClientes");

    if (!resultado) {
        return;
    }

    if (clientesEncontrados.length === 0) {

        resultado.innerHTML = `
            <p class="nenhum-cliente">
                Nenhum cliente encontrado.
            </p>
        `;

        return;

    }

    resultado.innerHTML = clientesEncontrados.map(cliente => `

        <div class="cliente-encontrado">

            <div class="cliente-info">

                <h3>
                    👤 ${cliente.nome}
                </h3>

                <p>
                    <strong>CPF:</strong>
                    ${cliente.cpf}
                </p>

                <p>
                    <strong>Telefone:</strong>
                    ${cliente.telefone}
                </p>

                <p>
                    <strong>E-mail:</strong>
                    ${cliente.email}
                </p>

            </div>

            <button
                class="btn-ver-cliente"
                onclick="verCliente(${cliente.id})"
            >
                <i class="fa-solid fa-eye"></i>
                Ver cliente
            </button>

        </div>

    `).join("");

}

function editarCliente(id) {

    const cliente = clientesEncontrados.find(
        cliente => cliente.id === id
    );

    if (!cliente) {
        alert("Cliente não encontrado.");
        return;
    }

    const resultado = document.getElementById("resultadoClientes");

    resultado.innerHTML = `

        <div class="detalhes-cliente">

            <div class="cabecalho-cliente">

                <div>

                    <span class="modal-subtitulo">
                        Editando cliente
                    </span>

                    <h2>
                        ✏️ ${cliente.nome}
                    </h2>

                </div>

            </div>

            <div class="grid-modal">

                <div class="info-box">

                    <h3>
                        👤 Informações pessoais
                    </h3>

                    <label>Nome</label>

                    <input
                        type="text"
                        id="editarNome"
                        value="${cliente.nome}"
                    >

                    <label>CPF</label>

                    <input
                        type="text"
                        id="editarCpf"
                        value="${cliente.cpf}"
                    >

                </div>

                <div class="info-box">

                    <h3>
                        📞 Contato
                    </h3>

                    <label>Telefone</label>

                    <input
                        type="text"
                        id="editarTelefone"
                        value="${cliente.telefone}"
                    >

                    <label>E-mail</label>

                    <input
                        type="email"
                        id="editarEmail"
                        value="${cliente.email}"
                    >

                </div>

            </div>

            <div class="acoes-cliente">

                <button
                    class="btn-voltar-cliente"
                    onclick="verCliente(${cliente.id})"
                >
                    <i class="fa-solid fa-xmark"></i>
                    Cancelar
                </button>

                <button
                    class="btn-editar-cliente"
                    onclick="salvarCliente(${cliente.id})"
                >
                    <i class="fa-solid fa-floppy-disk"></i>
                    Salvar alterações
                </button>

            </div>

        </div>

    `;

}
async function salvarCliente(id) {

    const nome = document.getElementById("editarNome").value.trim();
    const cpf = document.getElementById("editarCpf").value.trim();
    const telefone = document.getElementById("editarTelefone").value.trim();
    const email = document.getElementById("editarEmail").value.trim();

    if (!nome || !cpf || !telefone || !email) {

        alert("Preencha todos os campos.");
        return;

    }

    try {

        const resposta = await fetch(
            `http://127.0.0.1:8000/api/clientes/${id}/`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    nome: nome,
                    cpf: cpf,
                    telefone: telefone,
                    email: email
                })
            }
        );

        const clienteAtualizado = await resposta.json();

        if (!resposta.ok) {

            console.error(clienteAtualizado);

            alert(
                "Não foi possível atualizar o cliente."
            );

            return;

        }

        // Atualiza o cliente na lista que já carregamos
        const indice = clientesEncontrados.findIndex(
            cliente => cliente.id === id
        );

        if (indice !== -1) {

            clientesEncontrados[indice] = clienteAtualizado;

        }

        alert("Cliente atualizado com sucesso!");

        // Volta para a tela de detalhes
        verCliente(id);

    } catch (erro) {

        console.error(erro);

        alert(
            "Erro ao conectar com o servidor."
        );

    }

}


function abrirConfiguracoes() {

    const modal = document.getElementById("modalConfiguracoes");

    if (modal) {
        modal.style.display = "flex";
    }

}


function fecharConfiguracoes() {

    const modal = document.getElementById("modalConfiguracoes");

    if (modal) {
        modal.style.display = "none";
    }

}

function carregarProximaReserva() {

    const conteudo =
        document.getElementById("conteudoProximaReserva");

    if (!conteudo) {
        return;
    }

    const hoje = new Date();

    hoje.setHours(0, 0, 0, 0);

    const reservasFuturas = todasReservas.filter(reserva => {

        const dataReserva =
            new Date(reserva.data_reserva + "T00:00:00");

        return (
            reserva.status_nome === "CONFIRMADA" &&
            dataReserva >= hoje
        );

    });

    reservasFuturas.sort((a, b) => {

        const dataA =
            new Date(a.data_reserva + "T00:00:00");

        const dataB =
            new Date(b.data_reserva + "T00:00:00");

        return dataA - dataB;

    });

    if (reservasFuturas.length === 0) {

        conteudo.innerHTML = `

            <div class="sem-proxima-reserva">

                <i class="fa-solid fa-calendar-xmark"></i>

                <p>
                    Nenhuma próxima reserva confirmada.
                </p>

            </div>

        `;

        return;

    }

    const reserva = reservasFuturas[0];

    const dataFormatada =
        new Date(
            reserva.data_reserva + "T00:00:00"
        ).toLocaleDateString(
            "pt-BR"
        );

    conteudo.innerHTML = `

        <div class="proxima-reserva-card">

            <div class="proxima-cliente">

                <h3>
                    👤 ${reserva.cliente_nome}
                </h3>

                <p>
                    Código: ${reserva.codigo_reserva}
                </p>

                <div class="proxima-info">

                    <span>
                        <i class="fa-solid fa-calendar"></i>
                        ${dataFormatada}
                    </span>

                    <span>
                        <i class="fa-solid fa-clock"></i>
                        ${reserva.hora_inicio.slice(0, 5)}
                        às
                        ${reserva.hora_fim.slice(0, 5)}
                    </span>

                    <span>
                        <i class="fa-solid fa-circle-check"></i>
                        Confirmada
                    </span>

                </div>

            </div>

            <button
                class="btn-ver-proxima-reserva"
                onclick="abrirReserva('${reserva.codigo_reserva}')"
            >
                <i class="fa-solid fa-eye"></i>
                Ver Reserva
            </button>

        </div>

    `;

}

/*modal das informaçoes da laje */

function abrirInformacoesLaje() {

    const conteudo =
        document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    conteudo.innerHTML = `

        <button
            class="btn-voltar-config"
            onclick="voltarConfiguracoes()"
        >
            <i class="fa-solid fa-arrow-left"></i>
            Voltar
        </button>

        <div class="cabecalho-configuracoes">

            <span class="modal-subtitulo">
                Configurações
            </span>

            <h2>
                <i class="fa-solid fa-house"></i>
                Informações da Laje
            </h2>

            <p>
                Gerencie as informações principais da Laje do Modesto.
            </p>

        </div>

        <div class="form-configuracoes">

            <div class="info-box">

                <h3>
                    🏠 Informações
                </h3>

                <label>Nome</label>

                <input
                    type="text"
                    id="configNomeLaje"
                    value="Laje do Modesto"
                >

                <label>Telefone</label>

                <input
                    type="text"
                    id="configTelefoneLaje"
                    placeholder="(00) 00000-0000"
                >

                <label>E-mail</label>

                <input
                    type="email"
                    id="configEmailLaje"
                    placeholder="email@exemplo.com"
                >

                <label>Endereço</label>

                <input
                    type="text"
                    id="configEnderecoLaje"
                    placeholder="Digite o endereço"
                >

            </div>

            <div class="acoes-configuracoes">

                <button
                    class="btn-salvar-config"
                    onclick="salvarInformacoesLaje()"
                >
                    <i class="fa-solid fa-floppy-disk"></i>
                    Salvar alterações
                </button>

            </div>

        </div>

    `;

}

function voltarConfiguracoes() {

    console.log("Tela de configurações carregada");

    const conteudo =
        document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    conteudo.innerHTML = `

        <div class="cabecalho-configuracoes">

            <span class="modal-subtitulo">
                Administração
            </span>

            <h2>
                <i class="fa-solid fa-gear"></i>
                Configurações
            </h2>

            <p>
                Gerencie as configurações da Laje do Modesto.
            </p>

        </div>

        <div class="grid-configuracoes">

            <button
                class="card-configuracao"
                onclick="abrirInformacoesLaje()"
            >
                <i class="fa-solid fa-house"></i>

                <div>
                    <strong>Informações da Laje</strong>
                    <span>Nome, telefone, e-mail e endereço</span>
                </div>
            </button>

            <button
                class="card-configuracao"
                onclick="abrirValoresReserva()"
            >
                <i class="fa-solid fa-money-bill-wave"></i>

                <div>
                    <strong>Valores da Reserva</strong>
                    <span>Valor base e hora extra</span>
                </div>
            </button>

            <button class="card-configuracao">
                <i class="fa-solid fa-clock"></i>

                <div>
                    <strong>Horários</strong>
                    <span>Configure os horários das reservas</span>
                </div>
            </button>



            <button
                class="card-configuracao"
                onclick="abrirDiasBloqueados()"
            >
                <i class="fa-solid fa-calendar-xmark"></i>

                <div>
                    <strong>Dias Bloqueados</strong>
                    <span>Gerencie datas indisponíveis</span>
                </div>
            </button>




            <button
                class="card-configuracao"
                onclick="abrirAdicionais()"
            >
                <i class="fa-solid fa-champagne-glasses"></i>

                <div>
                    <strong>Adicionais</strong>
                    <span>Crie e gerencie serviços adicionais</span>
                </div>
            </button>


            <button
                class="card-configuracao"
                onclick="abrirCupons()"
            >
                <i class="fa-solid fa-ticket"></i>

                <div>
                    <strong>Cupons</strong>
                    <span>Crie e gerencie cupons de desconto</span>
                </div>
            </button>

        </div>

    `;

}

/*Configirações das reservas */

function abrirValoresReserva() {

    const conteudo =
        document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    conteudo.innerHTML = `

        <button
            class="btn-voltar-config"
            onclick="voltarConfiguracoes()"
        >
            <i class="fa-solid fa-arrow-left"></i>
            Voltar
        </button>

        <div class="cabecalho-configuracoes">

            <span class="modal-subtitulo">
                Configurações
            </span>

            <h2>
                <i class="fa-solid fa-money-bill-wave"></i>
                Valores da Reserva
            </h2>

            <p>
                Configure os valores utilizados nas reservas.
            </p>

        </div>

        <div class="form-configuracoes">

            <div class="info-box">

                <h3>
                    💰 Valores
                </h3>

                <label>
                    Valor base da reserva
                </label>

                <input
                    type="number"
                    id="configValorBase"
                    min="0"
                    step="0.01"
                    placeholder="Ex: 500.00"
                >

                <label>
                    Valor da hora extra
                </label>

                <input
                    type="number"
                    id="configValorHoraExtra"
                    min="0"
                    step="0.01"
                    value="60.00"
                >

            </div>

            <div class="acoes-configuracoes">

                <button
                    class="btn-salvar-config"
                    onclick="salvarValoresReserva()"
                >
                    <i class="fa-solid fa-floppy-disk"></i>
                    Salvar valores
                </button>

            </div>

        </div>

    `;

    carregarValoresReserva();

}

async function carregarValoresReserva() {

    try {

        const resposta = await fetch(
            `${API_URL}/configuracao-laje/reserva/`
        );

        if (!resposta.ok) {
            throw new Error(
                "Erro ao carregar valores da reserva."
            );
        }

        const dados = await resposta.json();

        const campoValorBase =
            document.getElementById("configValorBase");

        const campoValorHoraExtra =
            document.getElementById("configValorHoraExtra");

        if (campoValorBase) {

            campoValorBase.value =
                Number(dados.valor_base).toFixed(2);

        }

        if (campoValorHoraExtra) {

            campoValorHoraExtra.value =
                Number(dados.valor_hora_extra).toFixed(2);

        }

    } catch (erro) {

        console.error(
            "Erro ao carregar configurações:",
            erro
        );

        alert(
            "Não foi possível carregar os valores atuais."
        );

    }

}

async function salvarValoresReserva() {

    const campoValorBase =
        document.getElementById("configValorBase");

    const campoValorHoraExtra =
        document.getElementById("configValorHoraExtra");

    const valorBase =
        parseFloat(campoValorBase.value);

    const valorHoraExtra =
        parseFloat(campoValorHoraExtra.value);

    // Validação
    if (
        isNaN(valorBase) ||
        isNaN(valorHoraExtra)
    ) {

        alert("Preencha todos os valores corretamente.");
        return;

    }

    if (
        valorBase < 0 ||
        valorHoraExtra < 0
    ) {

        alert("Os valores não podem ser negativos.");
        return;

    }

    try {

        const resposta = await fetch(
            `${API_URL}/configuracao-laje/reserva/`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    valor_base: valorBase,
                    valor_hora_extra: valorHoraExtra
                })
            }
        );

        if (!resposta.ok) {

            throw new Error(
                "Erro ao salvar os valores."
            );

        }

        const dados = await resposta.json();

        console.log(
            "Valores atualizados:",
            dados
        );

        alert("Valores da reserva atualizados com sucesso!");

    } catch (erro) {

        console.error(
            "Erro ao salvar valores:",
            erro
        );

        alert(
            "Não foi possível salvar os valores."
        );

    }

}

async function abrirDiasBloqueados() {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    const modal = document.getElementById("modalConfiguracoes");

    if (modal) {
        modal.style.display = "flex";
    }

    conteudo.innerHTML = `
        <button
            class="btn-voltar-config"
            onclick="voltarConfiguracoes()"
        >
            <i class="fa-solid fa-arrow-left"></i>
            Voltar
        </button>

        <div class="cabecalho-configuracoes">
            <span class="modal-subtitulo">Configurações</span>

            <h2>
                <i class="fa-solid fa-calendar-xmark"></i>
                Dias Bloqueados
            </h2>

            <p>
                Cadastre as datas em que a Laje não estará disponível
                para reservas.
            </p>
        </div>

        <div class="form-configuracoes">
            <div class="info-box">
                <h3>📅 Bloquear uma data</h3>

                <label for="dataBloqueio">Data</label>
                <input
                    type="date"
                    id="dataBloqueio"
                    required
                >

                <label for="motivoBloqueio">Motivo (opcional)</label>
                <input
                    type="text"
                    id="motivoBloqueio"
                    maxlength="255"
                    placeholder="Ex.: manutenção ou evento particular"
                >

                <div class="acoes-configuracoes">
                    <button
                        class="btn-salvar-config"
                        onclick="salvarDiaBloqueado()"
                    >
                        <i class="fa-solid fa-lock"></i>
                        Bloquear data
                    </button>
                </div>
            </div>

            <div class="info-box">
                <h3>🗓️ Datas cadastradas</h3>
                <div id="listaDiasBloqueados">
                    Carregando datas...
                </div>
            </div>
        </div>
    `;

    await carregarDiasBloqueados();
}

window.abrirDiasBloqueados = abrirDiasBloqueados;


function abrirAdicionais() {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        console.error("Elemento conteudoConfiguracoes não encontrado.");
        return;
    }

    conteudo.innerHTML = `
        <div class="cabecalho-configuracoes">
            <button
                class="btn-voltar-config"
                onclick="voltarConfiguracoes()"
            >
                <i class="fa-solid fa-arrow-left"></i>
                Voltar
            </button>

            <h2>Gerenciar Adicionais</h2>
        </div>

        <div class="form-configuracoes">
            <h3>Cadastrar adicional</h3>

            <label for="adicionalNome">Nome</label>
            <input
                type="text"
                id="adicionalNome"
                placeholder="Ex.: Churrasqueira"
            >

            <label for="adicionalDescricao">Descrição</label>
            <textarea
                id="adicionalDescricao"
                placeholder="Descrição do adicional"
            ></textarea>

            <label for="adicionalValor">Valor (R$)</label>
            <input
                type="number"
                id="adicionalValor"
                min="0"
                step="0.01"
                placeholder="0,00"
            >

            <button
                class="btn-salvar-config"
                onclick="salvarAdicional()"
            >
                Salvar adicional
            </button>
        </div>

        <div class="acoes-configuracoes">
            <h3>Adicionais cadastrados</h3>
            <div id="listaAdicionais">
                Carregando adicionais...
            </div>
        </div>
    `;

    carregarAdicionais();
}

window.abrirAdicionais = abrirAdicionais;


function abrirCupons() {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        console.error("Elemento conteudoConfiguracoes não encontrado.");
        return;
    }

    conteudo.innerHTML = `
        <div class="cabecalho-configuracoes">
            <button
                class="btn-voltar-config"
                onclick="voltarConfiguracoes()"
            >
                <i class="fa-solid fa-arrow-left"></i>
                Voltar
            </button>

            <h2>Gerenciar Cupons</h2>
        </div>

        <div class="form-configuracoes">
            <h3>Cadastrar cupom</h3>

            <label for="cupomCodigo">Código do cupom</label>
            <input
                type="text"
                id="cupomCodigo"
                placeholder="Ex.: LAJE10"
            >

            <label for="cupomTipo">Tipo de desconto</label>
            <select id="cupomTipo">
                <option value="percentual">Percentual (%)</option>
                <option value="fixo">Valor fixo (R$)</option>
            </select>

            <label for="cupomValor">Valor do desconto</label>
            <input
                type="number"
                id="cupomValor"
                min="0.01"
                step="0.01"
                placeholder="Ex.: 10"
            >

            <label for="cupomUsoMaximo">Limite de utilizações</label>
            <input
                type="number"
                id="cupomUsoMaximo"
                min="1"
                step="1"
                placeholder="Ex.: 50"
            >

            <label for="cupomValidade">Data de validade</label>
            <input
                type="date"
                id="cupomValidade"
            >

            <button
                class="btn-salvar-config"
                onclick="salvarCupom()"
            >
                Salvar cupom
            </button>
        </div>

        <div class="acoes-configuracoes">
            <h3>Cupons cadastrados</h3>
            <div id="listaCupons">
                Carregando cupons...
            </div>
        </div>
    `;
    carregarCupons();
}

window.abrirCupons = abrirCupons;



async function salvarCupom() {
    const codigo = document.getElementById("cupomCodigo").value.trim().toUpperCase();
    const tipo = document.getElementById("cupomTipo").value;
    const valor = document.getElementById("cupomValor").value;
    const usoMaximo = document.getElementById("cupomUsoMaximo").value;
    const validade = document.getElementById("cupomValidade").value;

    const campoId = document.getElementById("cupomIdEdicao");
    const idEdicao = campoId?.value;
    const editando = Boolean(idEdicao);

    if (!codigo || !valor || !usoMaximo || !validade) {
        alert("Preencha todos os campos do cupom.");
        return;
    }

    if (Number(valor) <= 0 || Number(usoMaximo) < 1) {
        alert("O desconto e o limite de utilizações devem ser maiores que zero.");
        return;
    }

    if (!Number.isInteger(Number(usoMaximo))) {
        alert("O limite de utilizações deve ser um número inteiro.");
        return;
    }

    if (tipo === "percentual" && Number(valor) > 100) {
        alert("O desconto percentual não pode ultrapassar 100%.");
        return;
    }

    const cupom = {
        codigo: codigo,
        tipo_desconto: tipo,
        valor: Number(valor).toFixed(2),
        uso_maximo: Number(usoMaximo),
        validade: validade
    };

    if (!editando) {
        cupom.uso_atual = 0;
        cupom.ativo = true;
    }

    try {
        const url = editando
            ? `${API_URL}/cupons/${idEdicao}/`
            : `${API_URL}/cupons/`;

        const resposta = await fetch(url, {
            method: editando ? "PATCH" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(cupom)
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            console.error("Erro ao salvar cupom:", dados);
            alert(
                "Não foi possível salvar o cupom.\n" +
                JSON.stringify(dados, null, 2)
            );
            return;
        }

        alert(
            editando
                ? "Cupom atualizado com sucesso!"
                : "Cupom cadastrado com sucesso!"
        );

        document.getElementById("cupomCodigo").value = "";
        document.getElementById("cupomTipo").value = "percentual";
        document.getElementById("cupomValor").value = "";
        document.getElementById("cupomUsoMaximo").value = "";
        document.getElementById("cupomValidade").value = "";

        if (campoId) {
            campoId.value = "";
        }

        const titulo = document.querySelector(".form-configuracoes h3");
        const botaoSalvar = document.querySelector(
            ".form-configuracoes .btn-salvar-config"
        );

        if (titulo) {
            titulo.textContent = "Cadastrar cupom";
        }

        if (botaoSalvar) {
            botaoSalvar.textContent = "Salvar cupom";
        }

        await carregarCupons();

    } catch (erro) {
        console.error("Erro ao conectar com a API:", erro);
        alert("Não foi possível conectar ao servidor Django.");
    }
}

window.salvarCupom = salvarCupom;



async function carregarAdicionais() {
    const lista = document.getElementById("listaAdicionais");

    if (!lista) return;

    lista.textContent = "Carregando adicionais...";

    try {
        const resposta = await fetch(`${API_URL}/adicionais/`);

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();

        if (!Array.isArray(dados) || dados.length === 0) {
            lista.textContent = "Nenhum adicional cadastrado.";
            return;
        }

        lista.innerHTML = "";

        dados.forEach((adicional) => {
            const item = document.createElement("div");
            item.className = "cliente-resultado";

            const nome = document.createElement("strong");
            nome.textContent = adicional.nome;

            const descricao = document.createElement("p");
            descricao.textContent =
                adicional.descricao || "Sem descrição";

            const valor = document.createElement("p");
            valor.textContent = `Valor: ${Number(adicional.valor).toLocaleString(
                "pt-BR",
                { style: "currency", currency: "BRL" }
            )}`;

            const status = document.createElement("p");
            status.textContent = adicional.ativo
                ? "Status: Ativo"
                : "Status: Inativo";


            const acoes = document.createElement("div");
            acoes.style.display = "flex";
            acoes.style.gap = "10px";
            acoes.style.marginTop = "10px";


            const botaoEditar = document.createElement("button");
            botaoEditar.textContent = "Editar";
            botaoEditar.className = "btn-salvar-config";
            botaoEditar.onclick = () => editarAdicional(adicional);

            const botaoStatus = document.createElement("button");
            botaoStatus.textContent = adicional.ativo ? "Desativar" : "Ativar";
            botaoStatus.className = "btn-salvar-config";

            botaoStatus.onclick = () => alterarStatusAdicional(adicional);


            const botaoExcluir = document.createElement("button");
            botaoExcluir.textContent = "Excluir";
            botaoExcluir.className = "btn-salvar-config";

            botaoExcluir.style.backgroundColor = "#dc3545";

            botaoExcluir.onclick = () => excluirAdicional(adicional);

            acoes.append(botaoEditar, botaoStatus, botaoExcluir);



            item.append(nome, descricao, valor, status, acoes);
            lista.appendChild(item);

        });
    } catch (erro) {
        console.error("Erro ao carregar adicionais:", erro);
        lista.textContent =
            "Não foi possível carregar os adicionais. Verifique se o Django está rodando e se a API está acessível.";
    }
}


async function salvarAdicional() {
    const nome = document.getElementById("adicionalNome").value.trim();
    const descricao = document.getElementById("adicionalDescricao").value.trim();
    const valor = document.getElementById("adicionalValor").value;

    if (!nome) {
        alert("Informe o nome do adicional.");
        return;
    }

    if (valor === "" || !Number.isFinite(Number(valor)) || Number(valor) < 0) {
        alert("Informe um valor válido para o adicional.");
        return;
    }

    const botao = document.querySelector(
        "#conteudoConfiguracoes .btn-salvar-config"
    );

    if (botao) {
        botao.disabled = true;
        botao.textContent = "Salvando...";
    }

    try {
        const resposta = await fetch(`${API_URL}/adicionais/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nome: nome,
                descricao: descricao,
                valor: Number(valor).toFixed(2),
                ativo: true
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            const mensagem = Object.entries(dados)
                .map(([campo, erro]) => {
                    const detalhe = Array.isArray(erro)
                        ? erro.join(", ")
                        : typeof erro === "string"
                            ? erro
                            : JSON.stringify(erro);

                    return `${campo}: ${detalhe}`;
                })
                .join("\n");

            throw new Error(
                mensagem || `Erro ao cadastrar. Código: ${resposta.status}`
            );
        }

        alert("Adicional cadastrado com sucesso!");

        document.getElementById("adicionalNome").value = "";
        document.getElementById("adicionalDescricao").value = "";
        document.getElementById("adicionalValor").value = "";

        await carregarAdicionais();

    } catch (erro) {
        console.error("Erro ao salvar adicional:", erro);
        alert("Não foi possível cadastrar o adicional:\n" + erro.message);
    } finally {
        if (botao) {
            botao.disabled = false;
            botao.textContent = "Salvar adicional";
        }
    }
}

window.salvarAdicional = salvarAdicional;


async function alterarStatusAdicional(adicional) {
    const novoStatus = !adicional.ativo;

    const acao = novoStatus ? "ativar" : "desativar";

    const confirmar = confirm(
        `Deseja realmente ${acao} o adicional "${adicional.nome}"?`
    );

    if (!confirmar) return;

    try {
        const resposta = await fetch(
            `${API_URL}/adicionais/${adicional.id}/`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    ativo: novoStatus
                })
            }
        );

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                JSON.stringify(dados) || `Erro HTTP ${resposta.status}`
            );
        }

        alert(
            `Adicional ${novoStatus ? "ativado" : "desativado"} com sucesso!`
        );

        await carregarAdicionais();

    } catch (erro) {
        console.error("Erro ao alterar status do adicional:", erro);

        alert(
            "Não foi possível alterar o status do adicional.\n" +
            erro.message
        );
    }
}

window.alterarStatusAdicional = alterarStatusAdicional;


async function excluirAdicional(adicional) {
    const confirmar = confirm(
        `Tem certeza que deseja excluir o adicional "${adicional.nome}"?\n\nEssa ação não poderá ser desfeita.`
    );

    if (!confirmar) return;

    try {
        const resposta = await fetch(
            `${API_URL}/adicionais/${adicional.id}/`,
            {
                method: "DELETE"
            }
        );

        if (!resposta.ok) {
            const mensagem = await resposta.text();

            throw new Error(
                mensagem || `Erro HTTP ${resposta.status}`
            );
        }

        alert("Adicional excluído com sucesso!");

        await carregarAdicionais();

    } catch (erro) {
        console.error("Erro ao excluir adicional:", erro);

        alert(
            "Não foi possível excluir o adicional.\n" +
            erro.message
        );
    }
}

window.excluirAdicional = excluirAdicional;


function editarAdicional(adicional) {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) return;

    conteudo.innerHTML = `
        <div class="cabecalho-configuracoes">
            <button
                class="btn-voltar-config"
                onclick="abrirAdicionais()"
            >
                <i class="fa-solid fa-arrow-left"></i>
                Voltar
            </button>

            <h2>Editar Adicional</h2>
        </div>

        <div class="form-configuracoes">
            <label for="editarAdicionalNome">Nome</label>
            <input
                type="text"
                id="editarAdicionalNome"
                value="${String(adicional.nome || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}"
            >

            <label for="editarAdicionalDescricao">Descrição</label>
            <textarea id="editarAdicionalDescricao">${String(adicional.descricao || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</textarea>

            <label for="editarAdicionalValor">Valor (R$)</label>
            <input
                type="number"
                id="editarAdicionalValor"
                min="0"
                step="0.01"
                value="${Number(adicional.valor)}"
            >

            <button
                class="btn-salvar-config"
                onclick="salvarEdicaoAdicional(${Number(adicional.id)})"
            >
                Salvar alterações
            </button>
        </div>
    `;
}

window.editarAdicional = editarAdicional;


async function salvarEdicaoAdicional(id) {
    const nome = document
        .getElementById("editarAdicionalNome")
        .value.trim();

    const descricao = document
        .getElementById("editarAdicionalDescricao")
        .value.trim();

    const valor = document
        .getElementById("editarAdicionalValor")
        .value;

    if (!nome) {
        alert("Informe o nome do adicional.");
        return;
    }

    if (
        valor === "" ||
        !Number.isFinite(Number(valor)) ||
        Number(valor) < 0
    ) {
        alert("Informe um valor válido.");
        return;
    }

    try {
        const resposta = await fetch(`${API_URL}/adicionais/${id}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nome: nome,
                descricao: descricao,
                valor: Number(valor).toFixed(2)
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            const mensagem = Object.entries(dados)
                .map(([campo, erro]) => {
                    const detalhe = Array.isArray(erro)
                        ? erro.join(", ")
                        : typeof erro === "string"
                            ? erro
                            : JSON.stringify(erro);

                    return `${campo}: ${detalhe}`;
                })
                .join("\n");

            throw new Error(
                mensagem || `Erro HTTP ${resposta.status}`
            );
        }

        alert("Adicional atualizado com sucesso!");

        abrirAdicionais();
    } catch (erro) {
        console.error("Erro ao editar adicional:", erro);
        alert("Não foi possível atualizar o adicional:\n" + erro.message);
    }
}

window.salvarEdicaoAdicional = salvarEdicaoAdicional;


async function carregarDiasBloqueados() {
    const lista = document.getElementById("listaDiasBloqueados");

    if (!lista) {
        return;
    }

    try {
        const resposta = await fetch(
            `${API_URL}/dias-bloqueados/`
        );

        if (!resposta.ok) {
            throw new Error("Erro ao carregar dias bloqueados.");
        }

        const dias = await resposta.json();

        if (dias.length === 0) {
            lista.innerHTML = `
                <p class="mensagem-clientes">
                    Nenhum dia bloqueado cadastrado.
                </p>
            `;
            return;
        }

        lista.innerHTML = dias.map(dia => {
            const [ano, mes, diaNumero] = dia.data.split("-");

            const dataFormatada = `${diaNumero}/${mes}/${ano}`;

            return `
                <div class="cliente-resultado">
                    <div>
                        <strong>📅 ${dataFormatada}</strong>
                        <p>
                            Motivo: ${
                                dia.motivo || "Não informado"
                            }
                        </p>
                    </div>

                    <button
                        class="btn-voltar-cliente"
                        onclick="excluirDiaBloqueado(${dia.id})"
                    >
                        <i class="fa-solid fa-trash"></i>
                        Remover
                    </button>
                </div>
            `;
        }).join("");

    } catch (erro) {
        console.error("Erro ao carregar dias bloqueados:", erro);

        lista.innerHTML = `
            <p class="mensagem-clientes">
                Não foi possível carregar as datas bloqueadas.
            </p>
        `;
    }
}

window.carregarDiasBloqueados = carregarDiasBloqueados;


async function salvarDiaBloqueado() {
    const campoData = document.getElementById("dataBloqueio");
    const campoMotivo = document.getElementById("motivoBloqueio");

    const data = campoData.value;
    const motivo = campoMotivo.value.trim();

    if (!data) {
        alert("Selecione a data que deseja bloquear.");
        return;
    }

    try {
        const resposta = await fetch(
            `${API_URL}/dias-bloqueados/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    data: data,
                    motivo: motivo
                })
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok) {
            if (dados.data) {
                alert(
                    "Não foi possível bloquear essa data. " +
                    "Ela pode já estar cadastrada."
                );
            } else {
                alert("Erro ao cadastrar o bloqueio.");
            }

            console.error("Erro da API:", dados);
            return;
        }

        alert("Dia bloqueado com sucesso!");

        campoData.value = "";
        campoMotivo.value = "";

        await carregarDiasBloqueados();

    } catch (erro) {
        console.error("Erro ao salvar dia bloqueado:", erro);
        alert("Não foi possível conectar ao servidor.");
    }
}

window.salvarDiaBloqueado = salvarDiaBloqueado;


async function excluirDiaBloqueado(id) {
    const confirmar = confirm(
        "Tem certeza de que deseja remover este bloqueio?"
    );

    if (!confirmar) {
        return;
    }

    try {
        const resposta = await fetch(
            `${API_URL}/dias-bloqueados/${id}/`,
            {
                method: "DELETE"
            }
        );

        if (!resposta.ok) {
            throw new Error("Erro ao remover o bloqueio.");
        }

        alert("Bloqueio removido com sucesso!");

        await carregarDiasBloqueados();

    } catch (erro) {
        console.error("Erro ao remover dia bloqueado:", erro);

        alert("Não foi possível remover o bloqueio.");
    }
}

window.excluirDiaBloqueado = excluirDiaBloqueado;



async function carregarCupons() {
    const lista = document.getElementById("listaCupons");

    if (!lista) {
        console.error("Elemento listaCupons não encontrado.");
        return;
    }

    lista.textContent = "Carregando cupons...";

    try {
        const resposta = await fetch(`${API_URL}/cupons/`);

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();

        if (!Array.isArray(dados) || dados.length === 0) {
            lista.textContent = "Nenhum cupom cadastrado.";
            return;
        }

        lista.innerHTML = "";

        dados.forEach((cupom) => {
            const item = document.createElement("div");
            item.className = "cliente-resultado";

            const codigo = document.createElement("strong");
            codigo.textContent = cupom.codigo;

            const desconto = document.createElement("p");
            desconto.textContent =
                cupom.tipo_desconto === "percentual"
                    ? `Desconto: ${cupom.valor}%`
                    : `Desconto: R$ ${Number(cupom.valor).toFixed(2)}`;

            const usos = document.createElement("p");
            usos.textContent =
                `Utilizações: ${cupom.uso_atual}/${cupom.uso_maximo}`;

            const validade = document.createElement("p");
            validade.textContent =
                `Validade: ${new Date(cupom.validade + "T12:00:00").toLocaleDateString("pt-BR")}`;

            const status = document.createElement("p");
            status.textContent = cupom.ativo
                ? "Status: Ativo"
                : "Status: Inativo";

            const botao = document.createElement("button");
            botao.type = "button";
            botao.textContent = cupom.ativo
                ? "Desativar cupom"
                : "Ativar cupom";


            const botaoEditar = document.createElement("button");
            botaoEditar.type = "button";
            botaoEditar.textContent = "Editar";

            botaoEditar.addEventListener("click", () => {
                editarCupom(cupom);
            });


            botao.addEventListener("click", () => {
                alterarStatusCupom(cupom.id, !cupom.ativo);
            });

            item.append(codigo, desconto, usos, validade, status, botao, botaoEditar);
            lista.appendChild(item);
        });

    } catch (erro) {
        console.error("Erro ao carregar cupons:", erro);
        lista.textContent =
            "Erro ao carregar cupons. Confira o Console (F12).";
    }
}

window.carregarCupons = carregarCupons;


async function carregarCupons() {
    const lista = document.getElementById("listaCupons");

    if (!lista) {
        console.error("Elemento listaCupons não encontrado.");
        return;
    }

    lista.textContent = "Carregando cupons...";

    try {
        const resposta = await fetch(`${API_URL}/cupons/`);

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();

        if (!Array.isArray(dados) || dados.length === 0) {
            lista.textContent = "Nenhum cupom cadastrado.";
            return;
        }

        lista.innerHTML = "";

        dados.forEach((cupom) => {
            const item = document.createElement("div");
            item.className = "cliente-resultado";

            const codigo = document.createElement("strong");
            codigo.textContent = cupom.codigo;

            const desconto = document.createElement("p");
            desconto.textContent =
                cupom.tipo_desconto === "percentual"
                    ? `Desconto: ${cupom.valor}%`
                    : `Desconto: R$ ${Number(cupom.valor).toFixed(2)}`;

            const usos = document.createElement("p");
            usos.textContent =
                `Utilizações: ${cupom.uso_atual}/${cupom.uso_maximo}`;

            const validade = document.createElement("p");
            validade.textContent =
                `Validade: ${new Date(
                    cupom.validade + "T12:00:00"
                ).toLocaleDateString("pt-BR")}`;

            const status = document.createElement("p");
            status.textContent = cupom.ativo
                ? "Status: Ativo"
                : "Status: Inativo";

            const botaoEditar = document.createElement("button");
            botaoEditar.type = "button";
            botaoEditar.textContent = "Editar";

            botaoEditar.addEventListener("click", () => {
                editarCupom(cupom);
            });

            const botao = document.createElement("button");
            botao.type = "button";
            botao.textContent = cupom.ativo
                ? "Desativar cupom"
                : "Ativar cupom";

            botao.addEventListener("click", () => {
                alterarStatusCupom(cupom.id, !cupom.ativo);
            });

            item.append(
                codigo,
                desconto,
                usos,
                validade,
                status,
                botaoEditar,
                botao
            );

            lista.appendChild(item);
        });

    } catch (erro) {
        console.error("Erro ao carregar cupons:", erro);
        lista.textContent =
            "Erro ao carregar cupons. Confira o Console (F12).";
    }
}

window.carregarCupons = carregarCupons;


function editarCupom(cupom) {
    document.getElementById("cupomCodigo").value = cupom.codigo;
    document.getElementById("cupomTipo").value = cupom.tipo_desconto;
    document.getElementById("cupomValor").value = cupom.valor;
    document.getElementById("cupomUsoMaximo").value = cupom.uso_maximo;
    document.getElementById("cupomValidade").value = cupom.validade;

    // Guarda o ID do cupom que será editado
    let campoId = document.getElementById("cupomIdEdicao");

    if (!campoId) {
        campoId = document.createElement("input");
        campoId.type = "hidden";
        campoId.id = "cupomIdEdicao";

        const formulario = document.querySelector(".form-configuracoes");

        if (formulario) {
            formulario.appendChild(campoId);
        }
    }

    campoId.value = cupom.id;

    // Altera o título e o texto do botão
    const titulo = document.querySelector(".form-configuracoes h3");
    const botaoSalvar = document.querySelector(
        ".form-configuracoes .btn-salvar-config"
    );

    if (titulo) {
        titulo.textContent = "Editar cupom";
    }

    if (botaoSalvar) {
        botaoSalvar.textContent = "Salvar alterações";
    }

    // Leva a tela até o formulário
    document.querySelector(".form-configuracoes")?.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

window.editarCupom = editarCupom;
