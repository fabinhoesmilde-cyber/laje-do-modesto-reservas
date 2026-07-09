const form = document.getElementById("formReserva");
const mensagem = document.getElementById("mensagem");

const API_URL = "http://127.0.0.1:8000/api";
const STATUS_PENDENTE_ID = 1;

function horariosConflitam(inicioNovo, fimNovo, inicioExistente, fimExistente) {
    return inicioNovo < fimExistente && fimNovo > inicioExistente;
}

async function verificarDisponibilidade(data, horaInicio, horaFim) {
    const resposta = await fetch(`${API_URL}/reservas/`);
    const reservas = await resposta.json();

    return !reservas.some(reserva => {
        return (
            reserva.data_reserva === data &&
            horariosConflitam(
                horaInicio,
                horaFim,
                reserva.hora_inicio,
                reserva.hora_fim
            )
        );
    });
}
function formatarData(data) {
    const [ano, mes, dia] = data.split("-");
    return `${dia}/${mes}/${ano}`;
}

function formatarHora(hora) {
    return hora.substring(0, 5);
}
async function carregarReservas() {
    const listaReservas = document.getElementById("listaReservas");

    try {
        const resposta = await fetch(`${API_URL}/reservas/`);
        const reservas = await resposta.json();

        listaReservas.innerHTML = "";

        if (reservas.length === 0) {
            listaReservas.innerHTML =
                "<p>Nenhum horário indisponível no momento.</p>";
            return;
        }

        reservas.forEach(reserva => {

            // Não exibir reservas canceladas
            if (reserva.status_nome === "CANCELADA") {
                return;
            }

            const card = document.createElement("div");
            card.classList.add("reserva-card");

            card.innerHTML = `
                <strong>🔒 Horário indisponível</strong>
                <span>📅 Data: ${formatarData(reserva.data_reserva)}</span><br>
                <span>⏰ Horário: ${formatarHora(reserva.hora_inicio)} até ${formatarHora(reserva.hora_fim)}</span><br>
                <span>📌 Status: ${reserva.status_nome || "Reservado"}</span>
            `;

            listaReservas.appendChild(card);
        });

    } catch (erro) {
        console.error(erro);
        listaReservas.innerHTML =
            "<p>Erro ao carregar disponibilidade.</p>";
    }
}

// Carregar reservas ao iniciar a página
carregarReservas();

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    mensagem.textContent = "Verificando disponibilidade...";

    const dataReserva = document.getElementById("data_reserva").value;
    const horaInicio = document.getElementById("hora_inicio").value;
    const horaFim = document.getElementById("hora_fim").value;

    if (horaInicio >= horaFim) {
        mensagem.textContent = "A hora final deve ser maior que a hora inicial.";
        return;
    }

    const disponivel = await verificarDisponibilidade(
        dataReserva,
        horaInicio,
        horaFim
    );

    if (!disponivel) {
        mensagem.textContent = "Esse dia e horário já estão reservados.";
        return;
    }

    mensagem.textContent = "Enviando reserva...";

    const cliente = {
        nome: document.getElementById("nome").value,
        cpf: document.getElementById("cpf").value,
        telefone: document.getElementById("telefone").value,
        email: document.getElementById("email").value
    };

    try {
        const respostaCliente = await fetch(`${API_URL}/clientes/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(cliente)
        });

        if (!respostaCliente.ok) {
            mensagem.textContent = "Erro ao cadastrar cliente.";
            console.log(await respostaCliente.json());
            return;
        }

        const clienteCriado = await respostaCliente.json();

        const reserva = {
            cliente: clienteCriado.id,
            status: STATUS_PENDENTE_ID,
            cupom: null,
            data_reserva: dataReserva,
            hora_inicio: horaInicio,
            hora_fim: horaFim,
            valor_base: "700.00",
            valor_desconto: "0.00",
            valor_adicionais: "0.00",
            valor_total: "700.00",
            observacao: "Reserva criada pelo site"
        };

        const respostaReserva = await fetch(`${API_URL}/reservas/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(reserva)
        });

        if (!respostaReserva.ok) {
            mensagem.textContent = "Cliente criado, mas erro ao criar reserva.";
            console.log(await respostaReserva.json());
            return;
        }

        mensagem.textContent = "Reserva enviada com sucesso!";
        form.reset();
        carregarReservas();

    } catch (erro) {
        console.error(erro);
        mensagem.textContent = "Erro de conexão com a API.";
    }
});
async function cancelarReserva(idReserva) {
    const confirmar = confirm("Tem certeza que deseja cancelar esta reserva?");

    if (!confirmar) {
        return;
    }

    try {
        const respostaStatus = await fetch(`${API_URL}/status-reserva/`);
        const statusLista = await respostaStatus.json();

        const statusCancelada = statusLista.find(
            status => status.nome === "CANCELADA"
        );

        if (!statusCancelada) {
            alert("Status CANCELADA não encontrado.");
            return;
        }

        const resposta = await fetch(`${API_URL}/reservas/${idReserva}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                status: statusCancelada.id
            })
        });

        if (!resposta.ok) {
            alert("Erro ao cancelar reserva.");
            console.log(await resposta.json());
            return;
        }

        alert("Reserva cancelada com sucesso!");
        carregarReservas();

    } catch (erro) {
        console.error(erro);
        alert("Erro de conexão com a API.");
    }
}