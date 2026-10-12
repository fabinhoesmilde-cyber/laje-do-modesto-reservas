// ======================================
// WIZARD DE RESERVAS
// ======================================

// Etapas
const steps = document.querySelectorAll(".step");

// Botões
const btnNext = document.getElementById("btn-next");
const btnPrev = document.getElementById("btn-prev");

// Barra de progresso
const progressFill = document.querySelector(".progress-fill");

// Informações
const stepNumber = document.getElementById("step-number");
const stepTitle = document.getElementById("step-title");

// Etapa atual
let currentStep = 0;

// Nome das etapas
const titles = [
    "Calendário",
    "Horário",
    "Horas adicionais",
    "Adicionais",
    "Dados do Cliente",
    "Termos",
    "Resumo"
];

// ===============================
// Inicialização
// ===============================

document.addEventListener("DOMContentLoaded", () => {

    btnNext.addEventListener("click", avancarEtapa);
    btnPrev.addEventListener("click", voltarEtapa);

    const btnNovaReserva = document.getElementById("btn-nova-reserva");

    if (btnNovaReserva) {

        btnNovaReserva.addEventListener("click", () => {

            fecharSucesso();

            // Volta para o início do wizard
            currentStep = 0;
            updateWizard();

        });

    }

    updateWizard();

});

// ===============================
// Avançar
// ===============================

function avancarEtapa() {

    if (!validarEtapaAtual()) {
        return;
    }

    if (currentStep < steps.length - 1) {

        currentStep++;

        updateWizard();

    } else {

        finalizarReserva();

    }

}

// ===============================
// Voltar
// ===============================

function voltarEtapa() {

    if (currentStep > 0) {

        currentStep--;

        updateWizard();

    }

}

// ===============================
// Validação
// ===============================

function validarEtapaAtual() {

    switch (currentStep) {

        case 0:

            if (!reserva.getData()) {

                alert("Selecione uma data para continuar.");
                return false;

            }

            break;

        case 1:

            if (!reserva.getHorario()) {

                alert("Selecione um horário para continuar.");
                return false;

            }

            break;

        case 2:

            // Horas extras
            break;

        case 3:

            // Adicionais
            break;

        case 4:

            if (!cliente.mostrarErros()) {

                alert("Preencha corretamente os dados do cliente.");
                return false;

            }

            break;

        case 5:

            const aceitou = document.getElementById("aceitar-termos");

            if (!aceitou.checked) {

                alert("Você deve aceitar os termos da locação.");
                return false;

            }

            break;

    }

    return true;

}

// ===============================
// Atualiza Interface
// ===============================

function updateWizard() {

    steps.forEach(step => {

        step.classList.remove("active");

    });

    steps[currentStep].classList.add("active");

    if (currentStep === 6 && typeof resumoFinal !== "undefined") {

        resumoFinal.atualizar();

    }

    stepNumber.textContent =
        `Etapa ${currentStep + 1} de ${steps.length}`;

    stepTitle.textContent =
        titles[currentStep];

    const porcentagem =
        ((currentStep + 1) / steps.length) * 100;

    progressFill.style.width =
        porcentagem + "%";

    btnPrev.style.visibility =
        currentStep === 0 ? "hidden" : "visible";

    if (currentStep === steps.length - 1) {

        btnNext.textContent = "Finalizar Reserva";

    } else {

        btnNext.textContent = "Próximo →";

    }

}

// ===============================
// Finalizar Reserva
// ===============================

async function finalizarReserva() {

    const resumo = reservaService.calcularResumo();
    const cliente = reserva.getCliente();

    const dados = {

        nome: cliente.nome,
        cpf: cliente.cpf,
        telefone: cliente.telefone,
        email: cliente.email,
        convidados: cliente.convidados,

        data: reserva.getData(),
        hora_inicio: reserva.getHorario(),
        duracao: resumo.duracao,

        horas_extras: reserva.getHorasExtras(),

        valor_reserva: resumo.valorReserva,
        valor_adicionais: resumo.valorAdicionais,
        desconto: resumo.desconto,
        total: resumo.total,

        adicionais: reserva.getAdicionaisSelecionados().map(a => ({
            id: a.id
        }))

    };

    try {

        const resposta = await fetch(
            "http://127.0.0.1:8000/api/criar-reserva/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(dados)
            }
        );

        const resultado = await resposta.json();

        if (!resposta.ok) {

            alert(resultado.erro || "Erro ao criar reserva.");
            return;

        }

        mostrarSucesso(resultado.codigo_reserva);

        console.log(resultado);

    } catch (erro) {

        console.error(erro);

        alert("Não foi possível conectar ao servidor.");

    }

}

// ===============================
// Modal de Sucesso
// ===============================

function mostrarSucesso(codigo) {

    const modal = document.getElementById("modal-sucesso");

    if (!modal) {

        alert(`Reserva criada com sucesso!\n\nCódigo: ${codigo}`);
        return;

    }

    document.getElementById("codigo-reserva").textContent = codigo;

    modal.style.display = "flex";

}

// ===============================
// Fechar Modal
// ===============================

function fecharSucesso() {

    const modal = document.getElementById("modal-sucesso");

    if (modal) {

        modal.style.display = "none";

    }

}