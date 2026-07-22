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

            if(!reserva.getData()) {

                alert("Selecione uma data para continuar.");

                return false;

            }

            break;

        case 1:

            // Validação do horário virá depois

            break;

        case 2:

            // Horas adicionais

            break;

        case 3:

            // Adicionais

            break;

        case 4:

            // Dados do cliente

            break;

        case 5:

            // Termos

            break;

    }

    return true;

}

// ===============================
// Atualiza interface
// ===============================

function updateWizard() {

    steps.forEach(step => {

        step.classList.remove("active");

    });

    steps[currentStep].classList.add("active");

    stepNumber.textContent = `Etapa ${currentStep + 1} de ${steps.length}`;

    stepTitle.textContent = titles[currentStep];

    const porcentagem = ((currentStep + 1) / steps.length) * 100;

    progressFill.style.width = porcentagem + "%";

    btnPrev.style.visibility = currentStep === 0 ? "hidden" : "visible";

    if (currentStep === steps.length - 1) {

        btnNext.textContent = "Finalizar Reserva";

    } else {

        btnNext.textContent = "Próximo →";

    }

}

// ===============================
// Finalizar
// ===============================

function finalizarReserva() {

    console.log("Reserva pronta para envio:");

    console.log(reserva);

    alert("Em breve enviaremos os dados para o Django.");

}