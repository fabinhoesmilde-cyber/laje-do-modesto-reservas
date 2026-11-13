
 // ======================================
 // REGRAS DE NEGÓCIO DA RESERVA
 // ======================================

class ReservaService {

    constructor() {
        this.cupomAplicado = null;
    }

    /**
     * Calcula quantas horas extras
     * ainda podem ser contratadas.
     */
    calcularHorasExtrasDisponiveis(horario) {

        if (!horario) {
            return 0;
        }

        const horaInicio = parseInt(horario.split(":")[0], 10);
        const horaFim = horaInicio + 8;
        const limite = 29;

        return Math.max(0, limite - horaFim);
    }

    /**
     * Guarda o cupom validado pelo backend.
     */
    aplicarCupom(cupom) {
        this.cupomAplicado = cupom;
    }

    /**
     * Remove o cupom aplicado.
     */
    removerCupom() {
        this.cupomAplicado = null;
    }

    /**
     * Retorna o cupom aplicado.
     */
    getCupomAplicado() {
        return this.cupomAplicado;
    }

    /**
     * Calcula o resumo financeiro da reserva.
     */
    calcularResumo() {

        const configuracoes = reserva.getConfiguracoes() || {};
        const horasExtras = Number(reserva.getHorasExtras()) || 0;

        const duracaoPadrao =
            Number(
                configuracoes.duracao_reserva ??
                configuracoes.duracaoReserva ?? 8
            );

        const valorReserva =
            Number(
                configuracoes.valor_base ??
                configuracoes.valorBase ??
                configuracoes.valor_reserva ??
                configuracoes.valorReserva ??
                0
            );

        const valorHoraExtra =
            Number(
                configuracoes.valor_hora_extra ??
                configuracoes.valorHoraExtra ?? 0
            );

        const duracao = duracaoPadrao + horasExtras;

        const valorHorasExtras = horasExtras * valorHoraExtra;

        const valorAdicionais =
            reserva.getAdicionaisSelecionados()
                .reduce((total, adicional) => {
                    return total + Number(adicional.valor);
                }, 0);

        const subtotal =
            valorReserva +
            valorHorasExtras +
            valorAdicionais;

        const desconto =
            this.cupomAplicado
                ? Number(this.cupomAplicado.valor_desconto) || 0
                : 0;

        const total = Math.max(0, subtotal - desconto);

        return {
            duracao,
            valorReserva,
            valorHorasExtras,
            valorAdicionais,
            desconto,
            subtotal,
            total
        };
    }
}

const reservaService = new ReservaService();
