import SurferNFT from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Gastar FLOW para ganhar energia e subir
transaction(surferID: UInt64, flowAmount: UFix64) {
    let surfer: &SurferNFT.NFT
    let payment: @FlowToken.Vault

    prepare(signer: auth(Storage) &Account) {
        // Pegar a coleção
        let collection = signer.storage.borrow<&SurferNFT.Collection>(
            from: SurferNFT.CollectionStoragePath
        ) ?? panic("Coleção não encontrada!")

        // Pegar referência do surfista
        self.surfer = collection.borrowSurferNFT(id: surferID)
            ?? panic("Surfista não encontrado!")

        // Preparar pagamento
        let vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Vault de Flow não encontrado")

        self.payment <- vaultRef.withdraw(amount: flowAmount) as! @FlowToken.Vault
    }

    execute {
        let previousDepth = self.surfer.currentDepth
        let newDepth = self.surfer.boostEnergy(payment: <-self.payment)

        log("⚡ Boost de energia aplicado!")
        log("FLOW gasto: ".concat(flowAmount.toString()))
        log("Profundidade anterior: ".concat(previousDepth.toString()).concat("m"))
        log("Nova profundidade: ".concat(newDepth.toString()).concat("m"))

        if newDepth == 0 {
            log("🎉 PARABÉNS! Você chegou na superfície!")
        } else if newDepth <= 10 {
            log("🌅 Quase lá! Você está muito próximo da superfície!")
        } else if newDepth <= 50 {
            log("☀️ Ótimo! Águas rasas e seguras!")
        } else if newDepth <= 100 {
            log("🌊 Progresso bom! Continue subindo!")
        } else {
            log("⚠️ Ainda profundo! Considere mais boosts!")
        }
    }
}