import HackathonBadge from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Minta um badge de hackathon com prêmio inicial
transaction(participantName: String, eventName: String, initialPrize: UFix64) {
    let collection: &{HackathonBadge.HackathonBadgeCollectionPublic}
    let prizeVault: @FlowToken.Vault?

    prepare(signer: auth(Storage) &Account) {
        // Verifica se tem coleção, senão cria
        if signer.storage.type(at: HackathonBadge.CollectionStoragePath) == nil {
            let collection <- HackathonBadge.createEmptyCollection(nftType: Type<@HackathonBadge.NFT>())
            signer.storage.save(<-collection, to: HackathonBadge.CollectionStoragePath)

            let collectionCap = signer.capabilities.storage.issue<&{HackathonBadge.HackathonBadgeCollectionPublic}>(
                HackathonBadge.CollectionStoragePath
            )
            signer.capabilities.publish(collectionCap, at: HackathonBadge.CollectionPublicPath)
        }

        // Pega a coleção
        let cap = signer.capabilities.get<&{HackathonBadge.HackathonBadgeCollectionPublic}>(
            HackathonBadge.CollectionPublicPath
        )
        self.collection = cap.borrow() ?? panic("Não foi possível pegar a coleção")

        // Prepara prêmio inicial se necessário
        if initialPrize > 0.0 {
            let vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
                from: /storage/flowTokenVault
            ) ?? panic("Vault de Flow não encontrado")

            self.prizeVault <- vaultRef.withdraw(amount: initialPrize) as! @FlowToken.Vault
        } else {
            self.prizeVault <- nil
        }
    }

    execute {
        // Minta o NFT
        let id = HackathonBadge.mintNFT(
            participantName: participantName,
            eventName: eventName,
            recipient: self.collection,
            initialPrize: <-self.prizeVault
        )

        log("Badge mintado com ID: ".concat(id.toString()))
        log("Participante: ".concat(participantName))
        log("Evento: ".concat(eventName))
    }
}