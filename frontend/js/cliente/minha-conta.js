 const listaReservas = document.getElementById("listaReservas");
const mensagemConta = document.getElementById("mensagemConta");
const dadosConta = document.getElementById("dadosConta");
const formDados = document.getElementById("formDados");
const mensagemDados = document.getElementById("mensagemDados");

const NOMES_STATUS = {
    CONFIRMADA: "Confirmada",
    CANCELADA: "Cancelada",
    CANCELAMENTO_SOLICITADO: "Cancelamento aguardando aprovação",
    ALTERACAO_SOLICITADA: "Alteração aguardando aprovação"
};

function classeDoStatus(status) {
    if (status === "CONFIRMADA") return "st-confirmada";
    if (status === "CANCELADA") return "st-cancelada";
    return "st-pendente";
}

// ---------- dados do cliente ----------

function mostrarDados(cliente) {
    dadosConta.replaceChildren(
        criar("p", `E-mail: ${cliente.email}`),
        criar("p", `CPF: ${cliente.cpf}`)
    );

    document.getElementById("nome").value = cliente.nome;
    document.getElementById("telefone").value = cliente.telefone;
}

formDados.addEventListener("submit", async function (event) {
    event.preventDefault();

    mostrarMensagem(mensagemDados, "Salvando...", "");

    const resultado = await chamarApi("/cliente/meus-dados/", {
        metodo: "PATCH",
        autenticado: true,
        corpo: {
            nome: document.getElementById("nome").value.trim(),
            telefone: document.getElementById("telefone").value.trim()
        }
    });

    if (!resultado.ok) {
        mostrarMensagem(
            mensagemDados,
            resultado.dados.erro || "Não foi possível salvar.",
            "erro"
        );
        return;
    }

    mostrarDados(resultado.dados);
    mostrarMensagem(mensagemDados, "Dados atualizados.", "ok");
});

// ---------- reservas ----------

function linha(rotulo, valor) {
    const div = criar("div", null, "linha-info");
    div.append(criar("span", rotulo), criar("strong", valor));
    return div;
}

function fecharCaixas(cartao) {
    cartao.querySelectorAll(".caixa-acao").forEach((c) => c.remove());
}

function montarCartao(reserva) {
    const cartao = criar(
        "article", null, `cartao-reserva ${classeDoStatus(reserva.status)}`
    );

    cartao.append(criar("h3", `Reserva ${reserva.codigo_reserva}`));
    cartao.append(linha("Data", formatarData(reserva.data_reserva)));
    cartao.append(linha(
        "Horário",
        `${formatarHora(reserva.hora_inicio)} às ${formatarHora(reserva.hora_fim)}`
    ));
    cartao.append(linha("Valor total", formatarReais(reserva.valor_total)));

    const linhaStatus = criar("div", null, "linha-info");
    linhaStatus.append(
        criar("span", "Situação"),
        criar("span", NOMES_STATUS[reserva.status] || reserva.status, "selo-status")
    );
    cartao.append(linhaStatus);

    if (reserva.alteracao_solicitada) {
        const pedido = reserva.alteracao_solicitada;
        const hora = pedido.novo_horario_inicio
            ? ` às ${pedido.novo_horario_inicio}`
            : "";
        cartao.append(linha(
            "Alteração pedida",
            `${formatarData(pedido.nova_data)}${hora}`
        ));
    }

    if (reserva.taxa_cancelamento !== undefined) {
        cartao.append(linha(
            "Taxa de cancelamento",
            formatarReais(reserva.taxa_cancelamento)
        ));
        cartao.append(linha(
            "Valor a devolver",
            formatarReais(reserva.valor_reembolso)
        ));
    }

    if (reserva.pode_cancelar || reserva.pode_alterar) {
        const acoes = criar("div", null, "acoes-reserva");

        if (reserva.pode_alterar) {
            const botao = criar("button", "Alterar data ou horário", "btn-alterar");
            botao.type = "button";
            botao.addEventListener("click", () => abrirAlteracao(cartao, reserva));
            acoes.append(botao);
        }

        if (reserva.pode_cancelar) {
            const botao = criar("button", "Cancelar reserva", "btn-cancelar");
            botao.type = "button";
            botao.addEventListener("click", () => abrirCancelamento(cartao, reserva));
            acoes.append(botao);
        }

        cartao.append(acoes);
    }

    return cartao;
}

function abrirCancelamento(cartao, reserva) {
    fecharCaixas(cartao);

    const previa = reserva.previa_cancelamento;
    const caixa = criar("div", null, "caixa-acao");

    if (previa.dentro_do_prazo) {
        caixa.append(criar(
            "p",
            `Cancelamento sem taxa. Valor a devolver: ${formatarReais(previa.reembolso)}.`
        ));
    } else {
        caixa.append(criar(
            "p",
            `Faltam menos de 7 dias para o evento: será cobrada uma taxa de ` +
            `${formatarReais(previa.taxa)} e o valor a devolver é ` +
            `${formatarReais(previa.reembolso)}. O pedido depende de ` +
            `aprovação da Laje do Modesto.`
        ));
    }

    const aviso = criar("p", null, "msg");
    const acoes = criar("div", null, "acoes-reserva");

    const confirmar = criar("button", "Confirmar cancelamento", "btn-cancelar");
    confirmar.type = "button";
    confirmar.addEventListener("click", async () => {
        confirmar.disabled = true;
        mostrarMensagem(aviso, "Enviando...", "");

        const resultado = await chamarApi(
            `/cliente/minhas-reservas/${encodeURIComponent(reserva.codigo_reserva)}/cancelar/`,
            { metodo: "POST", autenticado: true }
        );

        if (!resultado.ok) {
            confirmar.disabled = false;
            mostrarMensagem(
                aviso,
                resultado.dados.erro || "Não foi possível cancelar.",
                "erro"
            );
            return;
        }

        await carregarReservas();
        mostrarMensagem(mensagemConta, resultado.dados.mensagem, "ok");
    });

    const voltar = criar("button", "Voltar", "btn-secundario");
    voltar.type = "button";
    voltar.addEventListener("click", () => caixa.remove());

    acoes.append(confirmar, voltar);
    caixa.append(aviso, acoes);
    cartao.append(caixa);
}

function abrirAlteracao(cartao, reserva) {
    fecharCaixas(cartao);

    const caixa = criar("div", null, "caixa-acao");
    caixa.append(criar(
        "p",
        "Escolha a nova data e o horário de início. A duração da sua festa " +
        "é mantida. O pedido depende de aprovação, e o seu horário atual " +
        "continua reservado até lá."
    ));

    const form = document.createElement("form");

    const rotuloData = criar("label", "Nova data");
    const campoData = document.createElement("input");
    campoData.type = "date";
    campoData.min = dataDeHoje();
    campoData.required = true;

    const rotuloHora = criar("label", "Novo horário de início");
    const campoHora = document.createElement("select");
    campoHora.required = true;
    campoHora.className = "campo-select";

    for (let hora = 8; hora <= 21; hora++) {
        const texto = `${String(hora).padStart(2, "0")}:00`;
        const opcao = criar("option", texto);
        opcao.value = texto;
        campoHora.append(opcao);
    }

    const aviso = criar("p", null, "msg");
    const acoes = criar("div", null, "acoes-reserva");

    const enviar = criar("button", "Enviar pedido", "btn-alterar");
    enviar.type = "submit";

    const voltar = criar("button", "Voltar", "btn-secundario");
    voltar.type = "button";
    voltar.addEventListener("click", () => caixa.remove());

    acoes.append(enviar, voltar);
    form.append(rotuloData, campoData, rotuloHora, campoHora, aviso, acoes);
    caixa.append(form);
    cartao.append(caixa);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        enviar.disabled = true;
        mostrarMensagem(aviso, "Enviando...", "");

        const resultado = await chamarApi(
            `/cliente/minhas-reservas/${encodeURIComponent(reserva.codigo_reserva)}/alterar/`,
            {
                metodo: "POST",
                autenticado: true,
                corpo: {
                    nova_data: campoData.value,
                    novo_horario_inicio: campoHora.value
                }
            }
        );

        if (!resultado.ok) {
            enviar.disabled = false;
            mostrarMensagem(
                aviso,
                resultado.dados.erro || "Não foi possível enviar o pedido.",
                "erro"
            );
            return;
        }

        await carregarReservas();
        mostrarMensagem(mensagemConta, resultado.dados.mensagem, "ok");
    });
}

async function carregarReservas() {
    const resultado = await chamarApi("/cliente/minhas-reservas/", {
        autenticado: true
    });

    if (!resultado.ok) {
        listaReservas.replaceChildren(criar(
            "p", resultado.dados.erro || "Não foi possível carregar as reservas."
        ));
        return;
    }

    if (resultado.dados.length === 0) {
        listaReservas.replaceChildren(
            criar("p", "Você ainda não tem reservas.")
        );
        return;
    }

    listaReservas.replaceChildren(...resultado.dados.map(montarCartao));
}

// ---------- sair e início ----------

document.getElementById("botaoSair").addEventListener("click", async () => {
    await chamarApi("/cliente/logout/", { metodo: "POST", autenticado: true });
    apagarToken();
    window.location.href = "entrar.html";
});

async function iniciar() {
    if (!lerToken()) {
        window.location.href = "entrar.html";
        return;
    }

    const dados = await chamarApi("/cliente/meus-dados/", { autenticado: true });

    if (!dados.ok) {
        mostrarMensagem(
            mensagemConta,
            dados.dados.erro || "Não foi possível carregar sua conta.",
            "erro"
        );
        return;
    }

    mostrarDados(dados.dados);
    await carregarReservas();
}

iniciar();