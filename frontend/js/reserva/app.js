class App {

    async iniciar() {

        try {

            console.log("Iniciando sistema...");

            const configuracoes =
                await configuracaoService.carregarConfiguracoes();

            reserva.setConfiguracoes(configuracoes);

            const adicionais =
                await adicionalService.carregarAdicionais();

            reserva.setAdicionaisDisponiveis(adicionais);

            console.log("Adicionais:");

            console.table(adicionais);

            console.log("Sistema iniciado com sucesso!");

        } catch (erro) {

            console.error(erro);

            alert("Erro ao iniciar o sistema.");

        }

    }

}

const app = new App();

document.addEventListener("DOMContentLoaded", () => {

    app.iniciar();

});