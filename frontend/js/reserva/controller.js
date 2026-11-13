// ======================================
// CONTROLLER DA RESERVA
// ======================================

class ReservaController {

    // ============================
    // DATA
    // ============================

    selecionarData(data) {

        console.log("Data recebida:", data);

        reserva.setData(data);

        console.log("Data salva:", reserva.getData());

    }

    // ============================
    // HORÁRIO
    // ============================

    selecionarHorario(horario) {

        reserva.setHorario(horario);

        const maximo =
            reservaService.calcularHorasExtrasDisponiveis(horario);

        reserva.setMaxHorasExtras(maximo);

    }

    // ============================
    // HORAS EXTRAS
    // ============================

    definirHorasExtras(horas) {

        reserva.setHorasExtras(horas);

    }

    // ============================
    // TOTAL
    // ============================

    definirTotal(total) {

        reserva.setTotal(total);

    }

    // ============================
    // RESET
    // ============================

    limparReserva() {

        reserva.reset();

    }

    // ============================
    // CONSULTAS
    // ============================

    obterReserva() {

        return reserva;

    }

    obterResumo() {

        return {
            data: reserva.getData(),
            horario: reserva.getHorario(),
            horasExtras: reserva.getHorasExtras(),
            total: reserva.getTotal()
        };

    }

}

// Instância única do controller
const controller = new ReservaController();