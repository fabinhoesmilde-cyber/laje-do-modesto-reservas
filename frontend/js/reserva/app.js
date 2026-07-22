class App {

    async iniciar() {

        try {

            console.log("Iniciando sistema...");

            const configuracoes =
                await configuracaoService.carregarConfiguracoes();

            reserva.setConfiguracoes(configuracoes);

            console.log("Configurações carregadas com sucesso!");

            console.log(reserva.getConfiguracoes());

        } catch (erro) {

            console.error(erro);

            alert("Erro ao carregar as configurações do sistema.");

        }

    }

}

const app = new App();

document.addEventListener("DOMContentLoaded", () => {

    app.iniciar();

});