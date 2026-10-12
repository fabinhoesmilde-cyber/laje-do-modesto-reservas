// ======================================
// RESUMO FINAL
// ======================================

class ResumoFinal {

    atualizar() {

        const resumo = reservaService.calcularResumo();

        const cliente = reserva.getCliente() || {};

        // ==========================
        // Evento
        // ==========================

        document.getElementById("final-data").textContent =
            reserva.getData() || "-";

        document.getElementById("final-horario").textContent =
            reserva.getHorario() || "-";

        document.getElementById("final-duracao").textContent =
            `${resumo.duracao || 0} horas`;

        // ==========================
        // Cliente
        // ==========================

        document.getElementById("final-nome").textContent =
            cliente.nome || "-";

        document.getElementById("final-cpf").textContent =
            cliente.cpf || "-";

        document.getElementById("final-telefone").textContent =
            cliente.telefone || "-";

        document.getElementById("final-email").textContent =
            cliente.email || "-";

        document.getElementById("final-convidados").textContent =
            cliente.convidados || 0;

        // ==========================
        // Valores
        // ==========================

        document.getElementById("final-reserva").textContent =
            `R$ ${resumo.valorReserva.toFixed(2)}`;

        document.getElementById("final-horas").textContent =
            `R$ ${resumo.valorHorasExtras.toFixed(2)}`;

        document.getElementById("final-valor-adicionais").textContent =
            `R$ ${resumo.valorAdicionais.toFixed(2)}`;

        document.getElementById("final-desconto").textContent =
            `R$ ${resumo.desconto.toFixed(2)}`;

        document.getElementById("final-total").textContent =
            `R$ ${resumo.total.toFixed(2)}`;

        // ==========================
        // Adicionais
        // ==========================

        const container = document.getElementById("final-adicionais");

        container.innerHTML = "";

        const adicionais = reserva.getAdicionaisSelecionados();

        if (adicionais.length === 0) {

            container.innerHTML = "<p>Nenhum adicional selecionado.</p>";

        } else {

            adicionais.forEach(adicional => {

                container.innerHTML += `
                    <p>✔ ${adicional.nome}</p>
                `;

            });

        }

    }

}

const resumoFinal = new ResumoFinal();