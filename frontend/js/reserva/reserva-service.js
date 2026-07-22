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

        const configuracoes = reserva.getConfiguracoes();

        const valorReserva = configuracoes.valorReserva;

        const valorHorasExtras =
            reserva.getHorasExtras() *
            configuracoes.valorHoraExtra;

        // Ainda vamos implementar
        const valorAdicionais = 0;
        const desconto = 0;

        const subtotal =
            valorReserva +
            valorHorasExtras +
            valorAdicionais;

        const total =
            subtotal - desconto;

        return {

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