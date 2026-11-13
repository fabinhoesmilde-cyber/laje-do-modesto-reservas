// ======================================
// CALENDÁRIO DA RESERVA
// ======================================

document.addEventListener("DOMContentLoaded", iniciarCalendario);

let calendar;

let datasBloqueadas = [];

// ======================================

// ======================================
// CARREGA DATAS BLOQUEADAS
// ======================================

async function carregarDatasBloqueadas() {

    try {

        const resposta = await fetch(
            "http://127.0.0.1:8000/api/reservas/"
        );

        if (!resposta.ok) {

            throw new Error("Erro ao carregar reservas.");

        }

        const reservas = await resposta.json();

        datasBloqueadas = reservas
            .filter(reserva => reserva.status_nome !== "CANCELADA")
            .map(reserva => reserva.data_reserva);

        console.log("Datas bloqueadas:");

        console.table(datasBloqueadas);

    } catch (erro) {

        console.error(erro);

    }

}

// ======================================

async function iniciarCalendario() {

    const calendarEl = document.getElementById("calendar-container");

    if (!calendarEl) {

        console.error("Elemento #calendar-container não encontrado.");

        return;

    }

    await carregarDatasBloqueadas();

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

dayCellDidMount: function(info) {

    const data = info.date.toISOString().split("T")[0];

    if (datasBloqueadas.includes(data)) {

        info.el.classList.add("dia-bloqueado");

    }

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