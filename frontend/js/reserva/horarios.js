// ======================================
// HORÁRIOS
// ======================================

const horarios = [

    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00"

];

document.addEventListener("DOMContentLoaded", carregarHorarios);

function carregarHorarios(){

    const container =
        document.getElementById("horarios-container");

    if(!container){
        return;
    }

    horarios.forEach(horario=>{

        const card =
            document.createElement("div");

        card.className="horario-card";

        card.textContent=horario;

        card.addEventListener("click",()=>{

            selecionarHorario(card,horario);

        });

        container.appendChild(card);

    });

}

function selecionarHorario(card,horario){

    document
        .querySelectorAll(".horario-card")
        .forEach(c=>{

            c.classList.remove("selected");

        });

    card.classList.add("selected");

    controller.selecionarHorario(horario);

}