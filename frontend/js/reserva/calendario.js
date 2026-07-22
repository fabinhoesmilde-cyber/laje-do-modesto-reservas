// ======================================
// CALENDÁRIO DA RESERVA
// ======================================

document.addEventListener("DOMContentLoaded", iniciarCalendario);

let calendar;

// ======================================

function iniciarCalendario() {

    const calendarEl = document.getElementById("calendar-container");

    if (!calendarEl) {

        console.error("Elemento #calendar-container não encontrado.");

        return;

    }

    calendar = new FullCalendar.Calendar(calendarEl, {

        locale: "pt-br",

        initialView: "dayGridMonth",

        height: "auto",

        selectable: true,

        initialDate: new Date(),

        validRange: {
            start: new Date()
        },

        headerToolbar: {

            left: "prev,next today",

            center: "title",

            right: ""

        },

        buttonText: {

            today: "Hoje"

        },

        dateClick: selecionarData

    });

    calendar.render();

}

// ======================================

function selecionarData(info) {

    controller.selecionarData(info.dateStr);

    destacarDataSelecionada(info.dateStr);

}

// ======================================

function destacarDataSelecionada(dataSelecionada) {

    const dias = document.querySelectorAll(".fc-daygrid-day");

    dias.forEach(dia => {

        dia.classList.remove("selected-day");

        if (dia.dataset.date === dataSelecionada) {

            dia.classList.add("selected-day");

        }

    });

}