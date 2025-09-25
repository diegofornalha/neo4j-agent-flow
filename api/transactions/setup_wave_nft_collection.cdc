import WaveNFT from 0x36395f9dde50ea27

/// Configura uma coleção WaveNFT para o usuário
transaction {
    prepare(signer: auth(Storage, Capabilities) &Account) {
        // Verifica se já existe uma coleção
        if signer.storage.type(at: WaveNFT.CollectionStoragePath) == nil {
            // Cria uma nova coleção
            let collection <- WaveNFT.createEmptyCollection()

            // Salva no storage
            signer.storage.save(<-collection, to: WaveNFT.CollectionStoragePath)

            // Cria capability pública
            let cap = signer.capabilities.storage.issue<&WaveNFT.Collection>(
                WaveNFT.CollectionStoragePath
            )
            signer.capabilities.publish(cap, at: WaveNFT.CollectionPublicPath)

            log("Coleção WaveNFT criada com sucesso!")
        } else {
            log("Coleção WaveNFT já existe")
        }
    }
}