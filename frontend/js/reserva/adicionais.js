class Adicionais {

    constructor() {

        this.container =
            document.getElementById("adicionais-container");

        reserva.addListener(() => {

            this.renderizar();

        });

    }

    renderizar() {

        const disponiveis =
            reserva.getAdicionaisDisponiveis();

        const selecionados =
            reserva.getAdicionaisSelecionados();

        const somProfissionalSelecionado =
            selecionados.some(
                item => item.nome === "Som Profissional para Eventos"
            );

        this.container.innerHTML = "";

        disponiveis.forEach(adicional => {

            const selecionado =
                selecionados.some(item => item.id === adicional.id);

            const desabilitado =
                somProfissionalSelecionado &&
                adicional.nome === "Som Ambiente";

            const card =
                document.createElement("div");

            card.className = "adicional-card";

            card.innerHTML = `
                <label>

                    <input
                        type="checkbox"
                        ${selecionado ? "checked" : ""}
                        ${desabilitado ? "disabled" : ""}>

                    <strong>${adicional.nome}</strong>

                    <p>${adicional.descricao}</p>

                    ${desabilitado ? `
                    <small class="adicional-info">
                        ✓ Incluso no Som Profissional para Eventos
                    </small>
                ` : ""}

                <span>
                    R$ ${Number(adicional.valor).toFixed(2)}
                </span>

                </label>
            `;

            const checkbox =
                card.querySelector("input");

            checkbox.addEventListener("change", () => {

                if (checkbox.checked) {

                    // Se selecionar o Som Profissional,
                    // remove o Som Ambiente
                    if (adicional.nome === "Som Profissional para Eventos") {

                        const ambiente =
                            reserva.getAdicionaisSelecionados()
                                .find(item => item.nome === "Som Ambiente");

                        if (ambiente) {

                            reserva.removerAdicional(ambiente.id);

                        }

                    }

                    reserva.adicionarAdicional(adicional);

                } else {

                    reserva.removerAdicional(adicional.id);

                }

            });

            this.container.appendChild(card);

        });

    }

}

const adicionais = new Adicionais();