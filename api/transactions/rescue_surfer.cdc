import SurferNFT from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Resgatar um novo surfista (primeira interação)
transaction(surferName: String, initialReward: UFix64) {
    let collection: &{SurferNFT.SurferCollectionPublic}
    let rewardVault: @FlowToken.Vault?

    prepare(signer: auth(Storage, Capabilities) &Account) {
        // Criar coleção se não existir
        if signer.storage.type(at: SurferNFT.CollectionStoragePath) == nil {
            let collection <- SurferNFT.createEmptyCollection(nftType: Type<@SurferNFT.NFT>())
            signer.storage.save(<-collection, to: SurferNFT.CollectionStoragePath)

            let cap = signer.capabilities.storage.issue<&{SurferNFT.SurferCollectionPublic}>(
                SurferNFT.CollectionStoragePath
            )
            signer.capabilities.publish(cap, at: SurferNFT.CollectionPublicPath)
        }

        // Pegar a coleção
        let cap = signer.capabilities.get<&{SurferNFT.SurferCollectionPublic}>(
            SurferNFT.CollectionPublicPath
        )
        self.collection = cap.borrow() ?? panic("Não foi possível acessar a coleção")

        // Preparar recompensa inicial
        if initialReward > 0.0 {
            let vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
                from: /storage/flowTokenVault
            ) ?? panic("Vault de Flow não encontrado")

            self.rewardVault <- vaultRef.withdraw(amount: initialReward) as! @FlowToken.Vault
        } else {
            self.rewardVault <- nil
        }
    }

    execute {
        // Resgatar o surfista
        let surferID = SurferNFT.rescueSurfer(
            name: surferName,
            wallet: self.collection.owner?.address ?? panic("Sem endereço"),
            collection: self.collection,
            initialReward: <-self.rewardVault
        )

        log("🏄 Surfista resgatado com sucesso!")
        log("Nome: ".concat(surferName))
        log("ID: ".concat(surferID.toString()))
        log("Profundidade inicial: 75m")
        log("Status: Médio - Continue explorando para subir!")
    }
}