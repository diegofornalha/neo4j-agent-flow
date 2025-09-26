import WaveEventNFT from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Registra um participante em um evento
transaction(participantName: String, eventName: String, amount: UFix64) {
    let collection: &WaveEventNFT.Collection
    let vault: @FlowToken.Vault

    prepare(signer: auth(Storage) &Account) {
        // Pega a coleção do usuário
        self.collection = signer.storage
            .borrow<&WaveEventNFT.Collection>(from: WaveEventNFT.CollectionStoragePath)
            ?? panic("Coleção WaveEventNFT não encontrada. Execute setup primeiro!")

        // Pega o vault de Flow tokens
        let vaultRef = signer.storage
            .borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Vault de Flow não encontrado")

        // Retira o pagamento
        self.vault <- vaultRef.withdraw(amount: amount) as! @FlowToken.Vault
    }

    execute {
        // Registra o participante
        WaveEventNFT.registerParticipant(
            participantName: participantName,
            eventName: eventName,
            recipient: self.collection,
            payment: <-self.vault
        )

        log("Participante '".concat(participantName).concat("' registrado no evento '").concat(eventName).concat("' com sucesso!"))
    }
}