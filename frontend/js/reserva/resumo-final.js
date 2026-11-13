
 // ======================================
 // RESUMO FINAL
 // ======================================

class ResumoFinal {

    constructor() {
        this.inicializado = false;
        this.validacaoEmAndamento = false;
        this.cupomValidado = false;
        this.ultimaValidacao = 0;
        this.timerValidacao = null;
    }

    inicializarCupom() {

        if (this.inicializado) return;

        const botao = document.getElementById("btn-aplicar-cupom");

        if (botao) {
            botao.addEventListener("click", () => {
                this.validarCupom();
            });
        }

        // Detecta alterações no estado da reserva.
        reserva.addListener(() => {
            if (this.cupomValidado) {
                this.agendarRevalidacao();
            }
        });

        this.inicializado = true;
    }

    agendarRevalidacao() {

        clearTimeout(this.timerValidacao);

        this.timerValidacao = setTimeout(() => {
            this.validarCupom(true);
        }, 400);
    }

    async validarCupom(silencioso = false) {

        const campo = document.getElementById("cupom-codigo");
        const mensagem = document.getElementById("cupom-mensagem");
        const botao = document.getElementById("btn-aplicar-cupom");

        if (!campo || !mensagem || !botao) return;

        const codigo = campo.value.trim().toUpperCase();

        if (!codigo) {
            reservaService.removerCupom();
            this.cupomValidado = false;

            mensagem.textContent = "Digite o código do cupom.";
            this.mostrarResumo();
            return;
        }

        if (this.validacaoEmAndamento) return;

        const resumo = reservaService.calcularResumo();
        const subtotalEnviado = resumo.subtotal.toFixed(2);
        const codigoRequisicao = ++this.ultimaValidacao;

        this.validacaoEmAndamento = true;

        if (!silencioso) {
            botao.disabled = true;
            mensagem.textContent = "Validando cupom...";
        }

        try {

            const resposta = await fetch(
                "http://127.0.0.1:8000/api/validar-cupom/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        cupom_codigo: codigo,
                        subtotal: subtotalEnviado
                    })
                }
            );

            const dados = await resposta.json();

            // Ignora respostas antigas.
            if (codigoRequisicao !== this.ultimaValidacao) return;

            if (!resposta.ok || !dados.valido) {

                reservaService.removerCupom();
                this.cupomValidado = false;

                mensagem.textContent =
                    dados.erro || "Não foi possível validar o cupom.";

                this.mostrarResumo();
                return;
            }

            // Só aplica a resposta se o subtotal ainda for o mesmo.
            const subtotalAtual =
                reservaService.calcularResumo().subtotal.toFixed(2);

            if (subtotalAtual !== subtotalEnviado) {
                this.agendarRevalidacao();
                return;
            }

            reservaService.aplicarCupom(dados);
            this.cupomValidado = true;
            campo.value = dados.cupom_codigo;

            mensagem.textContent =
                `Cupom ${dados.cupom_codigo} aplicado com sucesso!`;

            this.mostrarResumo();

        } catch (erro) {

            if (!silencioso) {
                mensagem.textContent =
                    "Não foi possível conectar ao servidor. Tente novamente.";
            }

            console.error("Erro ao validar cupom:", erro);

        } finally {

            this.validacaoEmAndamento = false;
            botao.disabled = false;

        }
    }

    mostrarResumo() {

        const resumo = reservaService.calcularResumo();

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
    }

    atualizar() {

        this.inicializarCupom();

        const cliente = reserva.getCliente() || {};

        document.getElementById("final-data").textContent =
            reserva.getData() || "-";

        document.getElementById("final-horario").textContent =
            reserva.getHorario() || "-";

        const resumo = reservaService.calcularResumo();

        document.getElementById("final-duracao").textContent =
            `${resumo.duracao || 0} horas`;

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

        const container = document.getElementById("final-adicionais");
        container.innerHTML = "";

        const adicionais = reserva.getAdicionaisSelecionados();

        if (adicionais.length === 0) {
            container.innerHTML = "<p>Nenhum adicional selecionado.</p>";
        } else {
            adicionais.forEach(adicional => {
                container.innerHTML += `<p>✔ ${adicional.nome}</p>`;
            });
        }

        this.mostrarResumo();
    }
}

const resumoFinal = new ResumoFinal();
