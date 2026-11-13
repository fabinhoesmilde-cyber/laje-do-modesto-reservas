const API_URL = "http://127.0.0.1:8000/api";

let reservas = [];

async function carregarReservas() {

    try {

        const resposta = await fetch(
            `${API_URL}/reservas/`
        );

        reservas = await resposta.json();

        console.log(reservas);

    } catch (erro) {

        console.error(erro);

    }

}

document.addEventListener(
    "DOMContentLoaded",
    iniciarAgenda
);

let calendar;

async function iniciarAgenda() {

    await carregarReservas();

    const calendarEl =
        document.getElementById("admin-calendar");

calendar = new FullCalendar.Calendar(calendarEl, {

    locale: "pt-br",

    buttonText: {
    today: "Hoje"
},

    initialView: "dayGridMonth",

    height: "auto",

    events: reservas.map(reserva => ({

        title: reserva.codigo_reserva,

        start: reserva.data_reserva,

        extendedProps: {

            codigo: reserva.codigo_reserva

        }

    })),

eventClick: function (info) {

    abrirReserva(
        info.event.extendedProps.codigo
    );

}

});

    calendar.render();

}
function voltarPainel() {
    window.location.href = "admin.html";
}