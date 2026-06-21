const API_URL = "http://127.0.0.1:8000/api";

const adminToken = localStorage.getItem("adminToken");

const adminUsername = localStorage.getItem("adminUsername");

if (!adminToken) {
    window.location.href = "admin-login.html";
}
const usuarioLogado =
    document.getElementById("usuarioLogado");

if (usuarioLogado) {
    usuarioLogado.textContent =
        `Bem-vindo, ${adminUsername}`;
}

const reservasAlteracao =
document.getElementById(
    "reservasAlteracao"
);

const reservasCancelamento =
document.getElementById(
    "reservasCancelamento"
);

const reservasConfirmadas =
document.getElementById(
    "reservasConfirmadas"
);

const reservasOutras =
document.getElementById(
    "reservasOutras"
);
const campoBuscaReserva =
document.getElementById(
    "campoBuscaReserva"
);
async function carregarReservas() {
    try {
        const resposta = await fetch(`${API_URL}/reservas/`);
        const reservas = await resposta.json();

        reservasAlteracao.innerHTML = "";
        reservasCancelamento.innerHTML = "";
        reservasConfirmadas.innerHTML = "";
        reservasOutras.innerHTML = "";

        reservas.forEach(reserva => {
            let botoes = "";
            let classeStatus = "";

            if (reserva.status_nome === "ALTERACAO_SOLICITADA") {

                classeStatus = "status-alteracao";

                botoes = `

                    <button onclick="aprovarAlteracao('${reserva.codigo_reserva}')">
                        Aprovar Alteração
                    </button>

                    <button onclick="rejeitarAlteracao('${reserva.codigo_reserva}')">
                        Rejeitar Alteração
                    </button>
                `;
            }
            if (reserva.status_nome === "CONFIRMADA") {
                classeStatus = "status-confirmada";
            }

            if (reserva.status_nome === "CANCELAMENTO_SOLICITADO") {

                classeStatus = "status-cancelamento";

                botoes = `

                    <button onclick="aprovarCancelamento('${reserva.codigo_reserva}')">
                        Aprovar Cancelamento
                    </button>

                    <button onclick="rejeitarCancelamento('${reserva.codigo_reserva}')">
                        Rejeitar Cancelamento
                    </button>
                `;
            }
            const cardReserva = `
                <div class="painel-reserva ${classeStatus}">
                    <h3>${reserva.cliente_nome}</h3>

                    <p><strong>Código:</strong> ${reserva.codigo_reserva}</p>
                    <p><strong>Data:</strong> ${reserva.data_reserva}</p>
                    <p><strong>Status:</strong> ${reserva.status_nome}</p>

                    ${botoes}
                </div>
            `;
            if (reserva.status_nome === "ALTERACAO_SOLICITADA") {
                reservasAlteracao.innerHTML += cardReserva;
            } else if (reserva.status_nome === "CANCELAMENTO_SOLICITADO") {
                reservasCancelamento.innerHTML += cardReserva;
            } else if (reserva.status_nome === "CONFIRMADA") {
                reservasConfirmadas.innerHTML += cardReserva;
            } else {
                reservasOutras.innerHTML += cardReserva;
            }

            
        });

    } catch (erro) {
        console.error(erro);
        reservasOutras.innerHTML = "Erro ao carregar reservas.";
    }
}

async function aprovarAlteracao(codigoReserva) {
    const confirmar = confirm("Deseja aprovar esta alteração de data?");

    if (!confirmar) return;

    try {
        const resposta = await fetch(`${API_URL}/aprovar-alteracao/`, {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            "Authorization": `Token ${adminToken}`
        },
            body: JSON.stringify({
                codigo_reserva: codigoReserva
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Erro ao aprovar alteração.");
            return;
        }

        alert(dados.mensagem);
        carregarReservas();

    } catch (erro) {
        console.error(erro);
        alert("Erro de conexão com a API.");
    }
}

async function rejeitarAlteracao(codigoReserva) {
    const confirmar = confirm("Deseja rejeitar esta alteração de data?");

    if (!confirmar) return;

    try {
        const resposta = await fetch(`${API_URL}/rejeitar-alteracao/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${adminToken}`
            },
            body: JSON.stringify({
                codigo_reserva: codigoReserva
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Erro ao rejeitar alteração.");
            return;
        }

        alert(dados.mensagem);
        carregarReservas();

    } catch (erro) {
        console.error(erro);
        alert("Erro de conexão com a API.");
    }
}

async function aprovarCancelamento(codigoReserva) {
    const confirmar = confirm("Deseja aprovar este cancelamento?");

    if (!confirmar) return;

    try {
        const resposta = await fetch(`${API_URL}/aprovar-cancelamento/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${adminToken}`
            },
            body: JSON.stringify({
                codigo_reserva: codigoReserva
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Erro ao aprovar cancelamento.");
            return;
        }

        alert(dados.mensagem);
        carregarReservas();

    } catch (erro) {
        console.error(erro);
        alert("Erro de conexão com a API.");
    }
}

async function rejeitarCancelamento(codigoReserva) {
    const confirmar = confirm("Deseja rejeitar este cancelamento?");

    if (!confirmar) return;

    try {
        const resposta = await fetch(`${API_URL}/rejeitar-cancelamento/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${adminToken}`
            },
            body: JSON.stringify({
                codigo_reserva: codigoReserva
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Erro ao rejeitar cancelamento.");
            return;
        }

        alert(dados.mensagem);
        carregarReservas();

    } catch (erro) {
        console.error(erro);
        alert("Erro de conexão com a API.");
    }
}
function logoutAdmin() {
    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminUsername");

    window.location.href = "admin-login.html";
}
function buscarReservaPorCodigo() {

    const codigo =
        campoBuscaReserva.value
        .trim()
        .toLowerCase();

    if (!codigo) {
        carregarReservas();
        return;
    }

    const cards =
        document.querySelectorAll(
            ".painel-reserva"
        );

    cards.forEach(card => {

        const texto =
            card.textContent.toLowerCase();

        if (texto.includes(codigo)) {

            card.style.display = "block";

        } else {

            card.style.display = "none";

        }

    });

}
function limparBuscaReserva() {

    campoBuscaReserva.value = "";

    carregarReservas();

}

carregarReservas();