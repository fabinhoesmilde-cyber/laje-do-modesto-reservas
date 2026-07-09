const formConsulta = document.getElementById("formConsultaReserva");
const resultadoConsulta = document.getElementById("resultadoConsulta");

const API_URL = "http://127.0.0.1:8000/api";

let ultimaConsulta = null;

function formatarData(data) {
    const [ano, mes, dia] = data.split("-");
    return `${dia}/${mes}/${ano}`;
}

function formatarHora(hora) {
    return hora.substring(0, 5);
}

formConsulta.addEventListener("submit", async function (event) {
    event.preventDefault();

    resultadoConsulta.innerHTML = "<p>Buscando reserva...</p>";

    const cpfDigitado = document.getElementById("cpfConsulta").value.trim();
    const codigoDigitado = document
        .getElementById("codigoReservaConsulta")
        .value
        .trim()
        .toUpperCase();

    try {
        const resposta = await fetch(`${API_URL}/consultar-reserva/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                cpf: cpfDigitado,
                codigo_reserva: codigoDigitado
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            resultadoConsulta.innerHTML = `<p>${dados.erro}</p>`;
            return;
        }

        ultimaConsulta = {
            cpf: cpfDigitado,
            codigo_reserva: codigoDigitado
        };

        resultadoConsulta.innerHTML = `
    <div class="painel-reserva">
        <h2>Minha Reserva</h2>

        <div class="linha-info">
            <span>Código</span>
            <strong>${dados.codigo_reserva}</strong>
        </div>

        <div class="linha-info">
            <span>Data</span>
            <strong>${formatarData(dados.data_reserva)}</strong>
        </div>

        <div class="linha-info">
            <span>Horário</span>
            <strong>${formatarHora(dados.hora_inicio)} às ${formatarHora(dados.hora_fim)}</strong>
        </div>

        <div class="linha-info">
            <span>Status</span>
            <strong>${dados.status}</strong>
        </div>

        <div class="acoes-reserva">
            <button onclick="solicitarCancelamento()" class="btn-cancelar">
                Solicitar cancelamento
            </button>

            <button onclick="abrirAlteracao()" class="btn-alterar">
                Solicitar alteração de data
            </button>
        </div>
    </div>
`;

    } catch (erro) {
        console.error(erro);
        resultadoConsulta.innerHTML = "<p>Erro ao consultar reserva.</p>";
    }
});

async function solicitarCancelamento() {
    if (!ultimaConsulta) {
        alert("Consulte uma reserva primeiro.");
        return;
    }

    const confirmar = confirm(
        "Deseja realmente solicitar o cancelamento desta reserva?"
    );

    if (!confirmar) {
        return;
    }

    try {
        const resposta = await fetch(`${API_URL}/solicitar-cancelamento/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(ultimaConsulta)
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Erro ao solicitar cancelamento.");
            return;
        }

        alert(dados.mensagem);

        resultadoConsulta.innerHTML += `
            <p><strong>Status atualizado:</strong> ${dados.status}</p>
        `;

    } catch (erro) {
        console.error(erro);
        alert("Erro de conexão com a API.");
    }
}
function abrirAlteracao() {

    const novaData = prompt(
        "Digite a nova data (AAAA-MM-DD):"
    );

    if (!novaData) return;

    const novoInicio = prompt(
        "Digite o novo horário inicial (HH:MM):"
    );

    if (!novoInicio) return;

    const novoFim = prompt(
        "Digite o novo horário final (HH:MM):"
    );

    if (!novoFim) return;

    solicitarAlteracao(
        novaData,
        novoInicio,
        novoFim
    );
}

async function solicitarAlteracao(
    novaData,
    novoInicio,
    novoFim
) {

    try {

        const resposta = await fetch(
            `${API_URL}/solicitar-alteracao/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    cpf: ultimaConsulta.cpf,
                    codigo_reserva:
                        ultimaConsulta.codigo_reserva,

                    nova_data: novaData,
                    novo_horario_inicio: novoInicio,
                    novo_horario_fim: novoFim
                })
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro);
            return;
        }

        alert(dados.mensagem);

    } catch (erro) {

        console.error(erro);

        alert(
            "Erro ao solicitar alteração."
        );
    }
}