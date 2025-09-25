import WaveNFT from 0x36395f9dde50ea27

/// Verifica a coleção de um usuário
access(all) fun main(address: Address): {String: AnyStruct} {
    let account = getAccount(address)

    // Tenta pegar a coleção pública
    let collectionRef = account.capabilities
        .borrow<&WaveNFT.Collection>(WaveNFT.CollectionPublicPath)

    if collectionRef == nil {
        return {
            "hasCollection": false,
            "nftIDs": [],
            "nftCount": 0
        }
    }

    let collection = collectionRef!
    let ids = collection.getIDs()

    // Pega informações de cada NFT
    let nfts: [{String: AnyStruct}] = []
    for id in ids {
        if let nft = collection.borrowNFT(id: id) {
            nfts.append(nft.getMetadata())
        }
    }

    return {
        "hasCollection": true,
        "nftIDs": ids,
        "nftCount": ids.length,
        "nfts": nfts
    }
}