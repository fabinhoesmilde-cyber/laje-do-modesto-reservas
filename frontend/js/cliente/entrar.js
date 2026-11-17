const formEntrar = document.getElementById("formEntrar");
const mensagemEntrar = document.getElementById("mensagemEntrar");
const botaoEntrar = document.getElementById("botaoEntrar");

formEntrar.addEventListener("submit", async function (event) {
    event.preventDefault();

    botaoEntrar.disabled = true;
    mostrarMensagem(mensagemEntrar, "Entrando...", "");

    const resultado = await chamarApi("/cliente/login/", {
        metodo: "POST",
        corpo: {
            email: document.getElementById("email").value.trim(),
            senha: document.getElementById("senha").value
        }
    });

    botaoEntrar.disabled = false;

    if (!resultado.ok) {
        mostrarMensagem(
            mensagemEntrar,
            resultado.dados.erro || "Não foi possível entrar.",
            "erro"
        );
        return;
    }

    guardarToken(resultado.dados.token);
    window.location.href = "minha-conta.html";
});