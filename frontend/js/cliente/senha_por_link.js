// Usado por confirmar-cadastro.html e redefinir-senha.html:
// o cliente chega pelo link do e-mail (?token=...) e escolhe uma senha.
// A página define, antes deste arquivo, a constante CONFIG_LINK:
//   { caminho: "/cliente/...", sucesso: "texto de fallback" }

const formSenha = document.getElementById("formSenha");
const mensagemSenha = document.getElementById("mensagemSenha");
const botaoSenha = document.getElementById("botaoSenha");
const linksFinais = document.getElementById("linksFinais");

const tokenDoLink = new URLSearchParams(window.location.search).get("token");

if (!tokenDoLink) {
    formSenha.hidden = true;
    mostrarMensagem(
        mensagemSenha,
        "Link inválido. Abra novamente o link que enviamos por e-mail.",
        "erro"
    );
}

formSenha.addEventListener("submit", async function (event) {
    event.preventDefault();

    const senha = document.getElementById("senha").value;
    const confirmacao = document.getElementById("confirmacao").value;

    if (senha !== confirmacao) {
        mostrarMensagem(mensagemSenha, "As senhas não são iguais.", "erro");
        return;
    }

    botaoSenha.disabled = true;
    mostrarMensagem(mensagemSenha, "Salvando...", "");

    const resultado = await chamarApi(CONFIG_LINK.caminho, {
        metodo: "POST",
        corpo: { token: tokenDoLink, senha: senha }
    });

    botaoSenha.disabled = false;

    if (!resultado.ok) {
        mostrarMensagem(
            mensagemSenha,
            resultado.dados.erro || "Não foi possível salvar a senha.",
            "erro"
        );
        return;
    }

    formSenha.hidden = true;
    linksFinais.hidden = false;
    mostrarMensagem(
        mensagemSenha,
        resultado.dados.mensagem || CONFIG_LINK.sucesso,
        "ok"
    );
});