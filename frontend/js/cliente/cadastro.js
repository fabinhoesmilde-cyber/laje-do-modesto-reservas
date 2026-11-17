const formCadastro = document.getElementById("formCadastro");
const mensagemCadastro = document.getElementById("mensagemCadastro");
const botaoCadastro = document.getElementById("botaoCadastro");

formCadastro.addEventListener("submit", async function (event) {
    event.preventDefault();

    botaoCadastro.disabled = true;
    mostrarMensagem(mensagemCadastro, "Enviando...", "");

    const resultado = await chamarApi("/cliente/cadastro/", {
        metodo: "POST",
        corpo: {
            nome: document.getElementById("nome").value.trim(),
            email: document.getElementById("email").value.trim(),
            cpf: document.getElementById("cpf").value.trim(),
            telefone: document.getElementById("telefone").value.trim()
        }
    });

    botaoCadastro.disabled = false;

    if (!resultado.ok) {
        mostrarMensagem(
            mensagemCadastro,
            resultado.dados.erro || "Não foi possível fazer o cadastro.",
            "erro"
        );
        return;
    }

    formCadastro.reset();
    mostrarMensagem(mensagemCadastro, resultado.dados.mensagem, "ok");
});