// ======================================
// ESTADO DA RESERVA
// ======================================

class ReservaState {

    constructor() {

        this.listeners = [];

        this.reset();

    }

    // ============================
    // RESET
    // ============================

    reset() {

        this.data = null;

        this.horario = null;

        this.horasExtras = 0;

        this.maxHorasExtras = 0;

        this.adicionais = {

            disponiveis: [],
            selecionados: []

        };

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
    // LIMITE DE HORAS EXTRAS
    // ============================

    setMaxHorasExtras(valor) {

        this.maxHorasExtras = valor;

        this.notify();

    }

    getMaxHorasExtras() {

        return this.maxHorasExtras;

    }

// ============================
// ADICIONAIS
// ============================

    setAdicionaisDisponiveis(adicionais) {

        this.adicionais.disponiveis = adicionais;

        this.notify();

    }

    getAdicionaisDisponiveis() {

        return this.adicionais.disponiveis;

    }

    getAdicionaisSelecionados() {

        return this.adicionais.selecionados;

    }

    adicionarAdicional(adicional) {

        const existe =
            this.adicionais.selecionados.some(item => item.id === adicional.id);

        if (!existe) {

            this.adicionais.selecionados.push(adicional);

            this.notify();

        }

    }

    removerAdicional(id) {

        this.adicionais.selecionados =
            this.adicionais.selecionados.filter(item => item.id !== id);

        this.notify();

    }

    // ============================
    // CONFIGURAÇÕES
    // ============================

setConfiguracoes(configuracoes) {

    this.configuracoes = {

        valorReserva: Number(
            configuracoes.valor_base ??
            configuracoes.valor_reserva ??
            0
        ),

        valorHoraExtra: Number(
            configuracoes.valor_hora_extra ??
            0
        ),

        duracaoReserva:
            configuracoes.duracao_reserva ?? 8,

        horarioLimite:
            configuracoes.horario_limite ?? 29

    };

    this.notify();

}

    getConfiguracoes() {

        return this.configuracoes;

    }

    // ============================
    // CLIENTE
    // ============================

    setCliente(cliente) {

        this.cliente = cliente;

        this.notify();

    }

    getCliente() {

        return this.cliente;

    }

    // ============================
    // PAGAMENTO
    // ============================

    setPagamento(pagamento) {

        this.pagamento = pagamento;

        this.notify();

    }

    getPagamento() {

        return this.pagamento;

    }

    // ============================
    // OBSERVER
    // ============================

    addListener(callback) {

        this.listeners.push(callback);

    }

    notify() {

        this.listeners.forEach(callback => callback(this));

    }

}

const reserva = new ReservaState();