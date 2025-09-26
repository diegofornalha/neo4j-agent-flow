import WaveEventPrizeNFT from 0x36395f9dde50ea27

/// Configura uma coleção WaveEventPrizeNFT
transaction {
    prepare(signer: auth(Storage, Capabilities) &Account) {
        // Verifica se já existe uma coleção
        if signer.storage.type(at: WaveEventPrizeNFT.CollectionStoragePath) == nil {
            // Cria uma nova coleção
            let collection <- WaveEventPrizeNFT.createEmptyCollection()

            // Salva no storage
            signer.storage.save(<-collection, to: WaveEventPrizeNFT.CollectionStoragePath)

            // Cria capability pública
            let cap = signer.capabilities.storage.issue<&WaveEventPrizeNFT.Collection>(
                WaveEventPrizeNFT.CollectionStoragePath
            )
            signer.capabilities.publish(cap, at: WaveEventPrizeNFT.CollectionPublicPath)

            log("Coleção WaveEventPrizeNFT criada com sucesso!")
        } else {
            log("Coleção WaveEventPrizeNFT já existe")
        }
    }
}