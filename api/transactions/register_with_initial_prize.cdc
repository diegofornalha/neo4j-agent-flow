import WaveEventPrizeNFT from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Registra participante com prêmio inicial
transaction(participantName: String, eventName: String, registrationFee: UFix64, initialPrize: UFix64) {
    let collection: &WaveEventPrizeNFT.Collection
    let paymentVault: @FlowToken.Vault
    let prizeVault: @FlowToken.Vault?

    prepare(signer: auth(Storage) &Account) {
        // Pega a coleção
        self.collection = signer.storage
            .borrow<&WaveEventPrizeNFT.Collection>(from: WaveEventPrizeNFT.CollectionStoragePath)
            ?? panic("Coleção WaveEventPrizeNFT não encontrada!")

        // Pega o vault de Flow
        let vaultRef = signer.storage
            .borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Vault de Flow não encontrado")

        // Retira pagamento e prêmio inicial
        self.paymentVault <- vaultRef.withdraw(amount: registrationFee) as! @FlowToken.Vault

        if initialPrize > 0.0 {
            self.prizeVault <- vaultRef.withdraw(amount: initialPrize) as! @FlowToken.Vault
        } else {
            self.prizeVault <- nil
        }
    }

    execute {
        // Registra participante com prêmio inicial
        WaveEventPrizeNFT.registerParticipantWithPrize(
            participantName: participantName,
            eventName: eventName,
            recipient: self.collection,
            payment: <-self.paymentVault,
            initialPrize: <-self.prizeVault
        )

        log("Participante '".concat(participantName).concat("' registrado com prêmio inicial de ").concat(initialPrize.toString()).concat(" FLOW!"))
    }
}