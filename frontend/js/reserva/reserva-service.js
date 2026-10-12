// ======================================
// REGRAS DE NEGÓCIO DA RESERVA
// ======================================

class ReservaService {

    /**
     * Calcula quantas horas extras
     * ainda podem ser contratadas.
     */
    calcularHorasExtrasDisponiveis(horario) {

        if (!horario) {
            return 0;
        }

        const horaInicio = parseInt(horario.split(":")[0], 10);

        // Reserva padrão possui 8 horas
        const horaFim = horaInicio + 8;

        // 05:00 do dia seguinte
        const limite = 29;

        return Math.max(0, limite - horaFim);

    }

    /**
     * Calcula o resumo financeiro da reserva.
     */
    calcularResumo() {

        const configuracoes = reserva.getConfiguracoes() || {};

        const horasExtras = Number(reserva.getHorasExtras()) || 0;

        // Aceita snake_case ou camelCase
        const duracaoPadrao =
            Number(configuracoes.duracao_reserva ??
                   configuracoes.duracaoReserva ?? 8);

        const valorReserva =
            Number(
                configuracoes.valor_base ??
                configuracoes.valorBase ??
                configuracoes.valor_reserva ??
                configuracoes.valorReserva ??
                0
            );

        const valorHoraExtra =
            Number(configuracoes.valor_hora_extra ??
                   configuracoes.valorHoraExtra ?? 0);

        const duracao = duracaoPadrao + horasExtras;

        const valorHorasExtras =
            horasExtras * valorHoraExtra;

        const valorAdicionais =
            reserva
                .getAdicionaisSelecionados()
                .reduce((total, adicional) => {

                    return total + Number(adicional.valor);

                }, 0);

        const desconto = 0;

        const subtotal =
            valorReserva +
            valorHorasExtras +
            valorAdicionais;

        const total =
            subtotal - desconto;

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