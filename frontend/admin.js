const API_URL = "http://127.0.0.1:8000/api";

const listaReservas =
document.getElementById(
    "listaReservasAdmin"
);

async function carregarReservas() {

    try {

        const resposta =
        await fetch(
            `${API_URL}/reservas/`
        );

        const reservas =
        await resposta.json();

        listaReservas.innerHTML = "";

        reservas.forEach(reserva => {

            listaReservas.innerHTML += `
                <div class="painel-reserva">

                    <h3>
                        ${reserva.cliente_nome}
                    </h3>

                    <p>
                        Código:
                        ${reserva.codigo_reserva}
                    </p>

                    <p>
                        Data:
                        ${reserva.data_reserva}
                    </p>

                    <p>
                        Status:
                        ${reserva.status_nome}
                    </p>

                </div>
            `;

        });

    }
    catch (erro) {

        console.error(erro);

        listaReservas.innerHTML =
        "Erro ao carregar reservas.";

    }

}

carregarReservas();