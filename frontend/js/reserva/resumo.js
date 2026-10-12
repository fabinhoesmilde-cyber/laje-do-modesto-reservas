// ======================================
// RESUMO DA RESERVA
// ======================================

function atualizarResumo() {

    const resumo = reservaService.calcularResumo();

    const configuracoes = reserva.getConfiguracoes();

    document.getElementById("summary-data").textContent =
        reserva.getData() || "—";

    document.getElementById("summary-horario").textContent =
        reserva.getHorario() || "—";

    document.getElementById("summary-duracao").textContent =
        `${configuracoes.duracaoReserva + reserva.getHorasExtras()} horas`;

    document.getElementById("summary-reserva").textContent =
        `R$ ${resumo.valorReserva.toFixed(2)}`;

    document.getElementById("summary-horas").textContent =
        `R$ ${resumo.valorHorasExtras.toFixed(2)}`;

    document.getElementById("summary-adicionais").textContent =
        `R$ ${resumo.valorAdicionais.toFixed(2)}`;

    document.getElementById("summary-desconto").textContent =
        `R$ ${resumo.desconto.toFixed(2)}`;

    document.getElementById("summary-total").textContent =
        `R$ ${resumo.total.toFixed(2)}`;

}

reserva.addListener(() => {

    atualizarResumo();

});