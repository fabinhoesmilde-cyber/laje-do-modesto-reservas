const formEsqueci = document.getElementById("formEsqueci");
const mensagemEsqueci = document.getElementById("mensagemEsqueci");
const botaoEsqueci = document.getElementById("botaoEsqueci");

formEsqueci.addEventListener("submit", async function (event) {
    event.preventDefault();

    botaoEsqueci.disabled = true;
    mostrarMensagem(mensagemEsqueci, "Enviando...", "");

    const resultado = await chamarApi("/cliente/esqueci-senha/", {
        metodo: "POST",
        corpo: { email: document.getElementById("email").value.trim() }
    });

    botaoEsqueci.disabled = false;

    if (!resultado.ok) {
        mostrarMensagem(
            mensagemEsqueci,
            resultado.dados.erro || "Não foi possível enviar o pedido.",
            "erro"
        );
        return;
    }

    mostrarMensagem(mensagemEsqueci, resultado.dados.mensagem, "ok");
});