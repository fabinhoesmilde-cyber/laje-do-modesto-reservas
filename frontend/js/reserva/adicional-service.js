// ======================================
// SERVIÇO DE ADICIONAIS
// ======================================

class AdicionalService {

    async carregarAdicionais() {

        const resposta =
            await fetch("http://127.0.0.1:8000/api/adicionais/");

        if (!resposta.ok) {
            throw new Error("Erro ao carregar adicionais.");
        }

        const adicionais = await resposta.json();

        return adicionais.filter(adicional => adicional.ativo === true);

    }

}

const adicionalService = new AdicionalService();