const formAdminLogin = document.getElementById("formAdminLogin");
const mensagemLogin = document.getElementById("mensagemLogin");

const API_URL = "http://127.0.0.1:8000/api";

formAdminLogin.addEventListener("submit", async function (event) {
    event.preventDefault();

    mensagemLogin.textContent = "Entrando...";

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const resposta = await fetch(`${API_URL}/admin-login/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            mensagemLogin.textContent = dados.erro || "Erro ao fazer login.";
            return;
        }

        localStorage.setItem("adminToken", dados.token);
        localStorage.setItem("adminUsername", dados.username);

        window.location.href = "admin.html";

    } catch (erro) {
        console.error(erro);
        mensagemLogin.textContent = "Erro de conexão com a API.";
    }
});