class ConfiguracaoService {

    async carregarConfiguracoes() {

        const resposta = await fetch(
            "http://127.0.0.1:8000/api/configuracoes/"
        );

        if (!resposta.ok) {
            throw new Error("Erro ao carregar configurações.");
        }

        return await resposta.json();
    }

}

const configuracaoService = new ConfiguracaoService();