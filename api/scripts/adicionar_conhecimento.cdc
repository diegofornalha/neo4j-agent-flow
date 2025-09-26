import SurfistaNFT from 0x25f823e2a115b2dc
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// Transação para adicionar conhecimento à bag do surfista mediante pagamento
/// Taxa varia conforme o tipo de conhecimento
///
transaction(nftID: UInt64, tipo: String, descricao: String, pontos: UInt64) {

    let surfista: &SurfistaNFT.NFT
    let pagamento: @FungibleToken.Vault

    prepare(signer: AuthAccount) {
        // Pegar a coleção do usuário
        let collection = signer.borrow<&SurfistaNFT.Collection>(from: SurfistaNFT.CollectionStoragePath)
            ?? panic("Não foi possível acessar a coleção de NFTs")

        // Pegar referência do NFT específico
        self.surfista = collection.borrowSurfista(id: nftID)
            ?? panic("Não foi possível encontrar a NFT do surfista")

        // Calcular taxa baseada no tipo
        var taxa = 0.1
        switch tipo {
            case "comando":
                taxa = 0.1
            case "arquivo":
                taxa = 0.2
            case "funcionalidade":
                taxa = 0.5
            case "tesouro":
                taxa = 1.0
            case "conquista":
                taxa = 2.0
        }

        // Preparar pagamento
        let vaultRef = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Não foi possível acessar o vault de FLOW")

        self.pagamento <- vaultRef.withdraw(amount: taxa)

        log("💰 Taxa para adicionar conhecimento: ".concat(taxa.toString()).concat(" FLOW"))
    }

    execute {
        // Adicionar conhecimento à bag com pagamento
        self.surfista.adicionarConhecimento(
            tipo: tipo,
            descricao: descricao,
            pontos: pontos,
            pagamento: <-self.pagamento
        )

        log("📚 Conhecimento adicionado à bag!")
        log("🎯 Tipo: ".concat(tipo))
        log("📝 Descrição: ".concat(descricao))
        log("💎 Pontos: ".concat(pontos.toString()))
        log("🏆 Pontos totais: ".concat(self.surfista.pontosTotal.toString()))
        log("💰 FLOW agora está no vault da NFT!")
    }
}