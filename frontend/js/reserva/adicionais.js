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

            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox'; checkbox.checked = selecionado; checkbox.disabled = desabilitado;
            const nome = document.createElement('strong'); nome.textContent = adicional.nome;
            const descricao = document.createElement('p'); descricao.textContent = adicional.descricao;
            label.append(checkbox, nome, descricao);
            if (desabilitado) { const info=document.createElement('small'); info.className='adicional-info'; info.textContent='✓ Incluso no Som Profissional para Eventos'; label.appendChild(info); }
            const valor=document.createElement('span'); valor.textContent=`R$ ${Number(adicional.valor).toFixed(2)}`; label.appendChild(valor);
            card.appendChild(label);

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