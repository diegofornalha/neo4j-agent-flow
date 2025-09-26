import SurfistaNFT from 0x25f823e2a115b2dc

/// Script para verificar o saldo de FLOW dentro da NFT do surfista
///
access(all) fun main(address: Address, nftID: UInt64): UFix64 {

    let account = getAccount(address)

    // Pegar a coleção pública
    let collection = account
        .getCapability(SurfistaNFT.CollectionPublicPath)
        .borrow<&{SurfistaNFT.SurfistaCollectionPublic}>()
        ?? panic("Não foi possível acessar a coleção")

    // Pegar a NFT do surfista
    let surfista = collection.borrowSurfista(id: nftID)
        ?? panic("Surfista não encontrado")

    // Retornar o saldo de FLOW armazenado na NFT
    return surfista.saldoRecompensas()
}