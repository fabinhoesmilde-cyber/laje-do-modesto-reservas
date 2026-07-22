// ======================================
// HORAS EXTRAS
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    reserva.addListener(renderizarHorasExtras);

    renderizarHorasExtras();

});

// ======================================

function renderizarHorasExtras() {

    const container =
        document.getElementById("horas-extras-container");

    if (!container) return;

    container.innerHTML = "";

    const maximo =
        reserva.getMaxHorasExtras();

    for (let i = 0; i <= maximo; i++) {

        const card =
            document.createElement("div");

        card.className = "hora-extra-card";

        card.textContent =
            i === 0
                ? "Sem horas extras"
                : `+${i} hora${i > 1 ? "s" : ""}`;

        if (i === reserva.getHorasExtras()) {

            card.classList.add("selected");

        }

        card.addEventListener("click", () => {

            controller.definirHorasExtras(i);

        });

        container.appendChild(card);

    }

}