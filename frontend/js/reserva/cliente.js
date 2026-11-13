// ======================================
// DADOS DO CLIENTE
// ======================================

class Cliente {

    constructor() {

        this.nome = document.getElementById("cliente-nome");
        this.cpf = document.getElementById("cliente-cpf");
        this.telefone = document.getElementById("cliente-telefone");
        this.email = document.getElementById("cliente-email");
        this.convidados = document.getElementById("cliente-convidados");

        this.inicializar();

    }

    inicializar() {

        // Nome
        this.nome.addEventListener("input", () => {

            this.salvar();
            this.mostrarErros();

        });

        // CPF
        this.cpf.addEventListener("input", () => {

            this.cpf.value = this.formatarCPF(this.cpf.value);

            this.salvar();
            this.mostrarErros();

        });

        // Telefone
        this.telefone.addEventListener("input", () => {

            this.telefone.value = this.formatarTelefone(this.telefone.value);

            this.salvar();
            this.mostrarErros();

        });

        // E-mail
        this.email.addEventListener("input", () => {

            this.salvar();
            this.mostrarErros();

        });

        // Convidados
        this.convidados.addEventListener("input", () => {

            this.salvar();
            this.mostrarErros();

        });

    }

    // ==========================
    // FORMATAÇÃO
    // ==========================

    formatarCPF(valor) {

        valor = valor.replace(/\D/g, "");
        valor = valor.substring(0, 11);

        valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
        valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
        valor = valor.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

        return valor;

    }

    formatarTelefone(valor) {

        valor = valor.replace(/\D/g, "");
        valor = valor.substring(0, 11);

        if (valor.length <= 10) {

            valor = valor.replace(/(\d{2})(\d)/, "($1) $2");
            valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

        } else {

            valor = valor.replace(/(\d{2})(\d)/, "($1) $2");
            valor = valor.replace(/(\d{5})(\d)/, "$1-$2");

        }

        return valor;

    }

    // ==========================
    // VALIDAÇÕES
    // ==========================

    validarEmail(email) {

        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    }

    validarCPF(cpf) {

        cpf = cpf.replace(/\D/g, '');

        if (cpf.length !== 11)
            return false;

        if (/^(\d)\1+$/.test(cpf))
            return false;

        let soma = 0;

        for (let i = 0; i < 9; i++) {

            soma += Number(cpf[i]) * (10 - i);

        }

        let resto = (soma * 10) % 11;

        if (resto === 10)
            resto = 0;

        if (resto !== Number(cpf[9]))
            return false;

        soma = 0;

        for (let i = 0; i < 10; i++) {

            soma += Number(cpf[i]) * (11 - i);

        }

        resto = (soma * 10) % 11;

        if (resto === 10)
            resto = 0;

        return resto === Number(cpf[10]);

    }

    validar() {

        const erros = [];

        if (this.nome.value.trim().length < 3)
            erros.push("Nome deve possuir pelo menos 3 caracteres.");

        if (!this.validarCPF(this.cpf.value))
            erros.push("CPF inválido.");

        if (!this.validarEmail(this.email.value))
            erros.push("E-mail inválido.");

        const telefone = this.telefone.value.replace(/\D/g, "");

        if (telefone.length < 10)
            erros.push("Telefone inválido.");

        if (Number(this.convidados.value) <= 0)
            erros.push("Informe a quantidade de convidados.");

        return {

            valido: erros.length === 0,

            erros

        };

    }

    // ==========================
    // SALVAR
    // ==========================

    salvar() {

        reserva.setCliente({

            nome: this.nome.value.trim(),

            cpf: this.cpf.value,

            telefone: this.telefone.value,

            email: this.email.value.trim(),

            convidados: Number(this.convidados.value)

        });

    }

    // ==========================
    // EXIBIR ERROS
    // ==========================

    mostrarErros() {

        const container = document.getElementById("cliente-erros");

        const resultado = this.validar();

        if (!container) {

            return resultado.valido;

        }

        if (resultado.valido) {

            container.innerHTML = "";

            return true;

        }

        container.innerHTML = resultado.erros
            .map(erro => `<p class="erro-validacao">${erro}</p>`)
            .join("");

        return false;

    }

}

const cliente = new Cliente();