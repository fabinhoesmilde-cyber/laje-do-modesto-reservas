// ======================================
// ESTADO DA RESERVA
// ======================================

class ReservaState {

    constructor() {

        this.listeners = [];

        this.reset();

    }

    reset() {

        this.data = null;

        this.horario = null;

        this.horasExtras = 0;

        this.maxHorasExtras = 0;

        this.adicionais = [];

        this.cliente = {

            nome: "",
            cpf: "",
            telefone: "",
            email: "",
            convidados: 0

        };

        this.pagamento = {

            metodo: null

        };

        this.configuracoes = {

            valorReserva: 0,

            valorHoraExtra: 0,

            duracaoReserva: 0,

            horarioLimite: ""

        };

        this.notify();

    }

    // ============================
    // DATA
    // ============================

    setData(data) {

        this.data = data;

        this.notify();

    }

    getData() {

        return this.data;

    }

    // ============================
    // HORÁRIO
    // ============================

    setHorario(horario) {

        this.horario = horario;

        this.notify();

    }

    getHorario() {

        return this.horario;

    }

    // ============================
    // HORAS EXTRAS
    // ============================

    setHorasExtras(horas) {

        this.horasExtras = horas;

        this.notify();

    }

    getHorasExtras() {

        return this.horasExtras;

    }

// ============================
// MÁXIMO DE HORAS EXTRAS
// ============================

setMaxHorasExtras(valor) {

    this.maxHorasExtras = valor;

    this.notify();

}

getMaxHorasExtras() {

    return this.maxHorasExtras;

}

// ============================
// CONFIGURAÇÕES
// ============================

    setConfiguracoes(configuracoes) {

        this.configuracoes = {

            valorReserva: Number(configuracoes.valor_reserva),

            valorHoraExtra: Number(configuracoes.valor_hora_extra),

            duracaoReserva: configuracoes.duracao_reserva,

            horarioLimite: configuracoes.horario_limite

        };

        this.notify();

    }

getConfiguracoes() {

    return this.configuracoes;

}

    addListener(callback) {

    this.listeners.push(callback);

}

notify() {

    this.listeners.forEach(callback => callback(this));

}

}

const reserva = new ReservaState();