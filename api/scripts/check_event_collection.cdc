import WaveEventNFT from 0x36395f9dde50ea27

/// Verifica a coleção de eventos de um usuário
access(all) fun main(address: Address): {String: AnyStruct} {
    let account = getAccount(address)

    // Tenta pegar a coleção pública
    let collectionRef = account.capabilities
        .borrow<&WaveEventNFT.Collection>(WaveEventNFT.CollectionPublicPath)

    if collectionRef == nil {
        return {
            "hasCollection": false,
            "nftIDs": [],
            "participantCount": 0,
            "activeEvents": WaveEventNFT.getActiveEvents()
        }
    }

    let collection = collectionRef!
    let ids = collection.getIDs()
    let badges = collection.getParticipantBadges()

    // Pega informações de cada NFT
    let participants: [{String: AnyStruct}] = []
    for id in ids {
        if let nft = collection.borrowNFT(id: id) {
            participants.append(nft.getMetadata())
        }
    }

    return {
        "hasCollection": true,
        "nftIDs": ids,
        "participantCount": ids.length,
        "badges": badges,
        "participants": participants,
        "activeEvents": WaveEventNFT.getActiveEvents()
    }
}