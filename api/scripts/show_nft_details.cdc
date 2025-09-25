import WaveNFT from 0x36395f9dde50ea27

/// Mostra detalhes de um NFT específico
access(all) fun main(address: Address, nftID: UInt64): {String: AnyStruct}? {
    let account = getAccount(address)

    // Pega a coleção pública
    let collectionRef = account.capabilities
        .borrow<&WaveNFT.Collection>(WaveNFT.CollectionPublicPath)
        ?? panic("Coleção não encontrada")

    // Pega o NFT
    if let nft = collectionRef.borrowNFT(id: nftID) {
        let metadata = nft.getMetadata()

        return {
            "id": metadata["id"] ?? "",
            "nome_registrado": metadata["name"] ?? "",  // Este é o nome que você escolhe
            "dono_original": metadata["originalOwner"] ?? "",
            "dono_atual": address,
            "data_criacao": metadata["mintedAt"] ?? "",
            "explicacao": "O NFT representa o NOME que você registrou (ex: 'blockchain'), não o nome da pessoa"
        }
    }

    return nil
}