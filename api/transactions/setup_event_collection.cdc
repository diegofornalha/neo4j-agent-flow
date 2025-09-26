import WaveEventNFT from 0x36395f9dde50ea27

/// Configura uma coleção WaveEventNFT para o usuário
transaction {
    prepare(signer: auth(Storage, Capabilities) &Account) {
        // Verifica se já existe uma coleção
        if signer.storage.type(at: WaveEventNFT.CollectionStoragePath) == nil {
            // Cria uma nova coleção
            let collection <- WaveEventNFT.createEmptyCollection()

            // Salva no storage
            signer.storage.save(<-collection, to: WaveEventNFT.CollectionStoragePath)

            // Cria capability pública
            let cap = signer.capabilities.storage.issue<&WaveEventNFT.Collection>(
                WaveEventNFT.CollectionStoragePath
            )
            signer.capabilities.publish(cap, at: WaveEventNFT.CollectionPublicPath)

            log("Coleção WaveEventNFT criada com sucesso!")
        } else {
            log("Coleção WaveEventNFT já existe")
        }
    }
}