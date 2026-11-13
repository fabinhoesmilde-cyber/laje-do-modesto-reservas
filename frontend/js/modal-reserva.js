function abrirReserva(codigoReserva) {

let listaReservas = [];

if (typeof todasReservas !== "undefined") {

    listaReservas = todasReservas;

} else if (typeof reservas !== "undefined") {

    listaReservas = reservas;

}

const reserva = listaReservas.find(
    r => r.codigo_reserva === codigoReserva
);

    if (!reserva) {
        alert("Reserva não encontrada.");
        return;
    }

    const modal = document.getElementById("modalReserva");
    const conteudoModal = document.getElementById("conteudoModal");

    let adicionaisHTML = "";

    if (reserva.adicionais && reserva.adicionais.length > 0) {

        adicionaisHTML = reserva.adicionais.map(adicional => `

            <div class="item-adicional">

                <div>

                    <strong>${adicional.nome}</strong>

                    <p>
                        Quantidade: ${adicional.quantidade}
                    </p>

                </div>

                <div>

                    <strong>

                        R$ ${adicional.valor_total}

                    </strong>

                </div>

            </div>

        `).join("");

    } else {

        adicionaisHTML = `

            <div class="sem-adicionais">

                Nenhum adicional contratado.

            </div>

        `;

    }
    const valorHoraExtra = 60;

    const valorHorasExtras =
        reserva.horas_extras * valorHoraExtra;

    conteudoModal.innerHTML = `

    <div class="cabecalho-modal">

        <div>

            <span class="modal-subtitulo">

                Reserva

            </span>

            <h2>

                👤 ${reserva.cliente_nome}

            </h2>

            <span class="codigo-modal">

                Código ${reserva.codigo_reserva}

            </span>

        </div>

        <div class="status-lateral">

            <span class="badge-status">

                ${reserva.status_nome}

            </span>

        </div>

    </div>

    <div class="grid-modal">

        <div class="info-box">

            <h3>

                👤 Cliente

            </h3>

                        <p>

                <strong>Nome</strong>

                ${reserva.cliente_nome}

            </p>

            <p>

                <strong>CPF</strong>

                ${reserva.cpf}

            </p>

            <p>

                <strong>Telefone</strong>

                ${reserva.telefone}

            </p>

            <p>

                <strong>E-mail</strong>

                ${reserva.email}

            </p>

        </div>

        <div class="info-box">

            <h3>

                📅 Reserva

            </h3>

            <p>

                <strong>Data</strong>

                ${reserva.data_reserva}

            </p>

            <p>

                <strong>Horário</strong>

                ${reserva.hora_inicio.slice(0, 5)}
                às
                ${reserva.hora_fim.slice(0, 5)}

            </p>

            <p>

                <strong>Status</strong>

                ${reserva.status_nome}

            </p>

            <p>

                <strong>Código</strong>

                ${reserva.codigo_reserva}

            </p>

        </div>

        <div class="info-box">

            <h3>

                💰 Financeiro

            </h3>

            <p>

                <strong>Valor Base</strong>

                R$ ${reserva.valor_base}

            </p>

            <p>

                <strong>Desconto</strong>

                R$ ${reserva.valor_desconto}

            </p>

            <p>

                <strong>Horas Extras</strong>

                R$ ${valorHorasExtras.toFixed(2)}

            </p>

            <p>

                <strong>Adicionais</strong>

                R$ ${reserva.valor_adicionais}

            </p>

            <p class="valor-total">

                R$ ${reserva.valor_total}

            </p>

          </div>

          <div class="info-box">

            <h3>

                ⏰ Tempo da Reserva

            </h3>

            <p>

                <strong>Horas Inclusas</strong>

                8 horas

            </p>

            <p>

                <strong>Horas Extras</strong>

                ${reserva.horas_extras} hora(s)

            </p>

            <p>

                <strong>Total Contratado</strong>

                ${8 + Number(reserva.horas_extras)} horas

            </p>

            <p>

                <strong>Horário</strong>

                ${reserva.hora_inicio.slice(0, 5)}
                às
                ${reserva.hora_fim.slice(0, 5)}

            </p>

        </div>

                <div class="info-box info-box-full">

            <h3>

                🎉 Adicionais Contratados

            </h3>

            ${adicionaisHTML}

        </div>

        <div class="info-box">

            <h3>

                🏷 Cupom

            </h3>

            <p>

                ${
                    reserva.cupom_codigo
                        ? reserva.cupom_codigo
                        : "Nenhum cupom aplicado"
                }

            </p>

        </div>

        <div class="info-box">

            <h3>

                📌 Status da Reserva

            </h3>

            <p>

                ${reserva.status_nome}

            </p>

        </div>

        <div class="info-box info-box-full">

            <h3>

                📝 Observações

            </h3>

            <p>

                ${
                    reserva.observacao
                        ? reserva.observacao
                        : "Nenhuma observação cadastrada."
                }

            </p>

        </div>

            </div>

    `;

    modal.style.display = "flex";

}
function fecharModal() {

    const modal = document.getElementById("modalReserva");

    if (modal) {

        modal.style.display = "none";

    }

}
window.abrirReserva = abrirReserva;
window.fecharModal = fecharModal;