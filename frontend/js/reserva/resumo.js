// ======================================
// RESUMO DA RESERVA
// ======================================

function atualizarResumo() {

    const itens = document.querySelectorAll(".summary-item span");

    if (itens.length < 4) {
        return;
    }

    const resumo = reservaService.calcularResumo();

    const configuracoes = reserva.getConfiguracoes();

    itens[0].textContent =
        reserva.getData() || "—";

    itens[1].textContent =
        reserva.getHorario() || "—";

    itens[2].textContent =
        `${configuracoes.duracaoReserva + reserva.getHorasExtras()} horas`;

    itens[3].textContent =
        `R$ ${resumo.total.toFixed(2)}`;

}
reserva.addListener(() => {

    atualizarResumo();

});