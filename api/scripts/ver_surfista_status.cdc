import SurfistaNFT from 0x25f823e2a115b2dc

/// Script para verificar o status completo de um surfista
///
access(all) fun main(address: Address, nftID: UInt64): {String: AnyStruct} {

    let account = getAccount(address)

    // Pegar a coleção pública
    let collection = account
        .getCapability(SurfistaNFT.CollectionPublicPath)
        .borrow<&{SurfistaNFT.SurfistaCollectionPublic}>()
        ?? panic("Não foi possível acessar a coleção")

    // Pegar a NFT do surfista
    let surfista = collection.borrowSurfista(id: nftID)
        ?? panic("Surfista não encontrado")

    // Calcular status de profundidade
    let profundidade = surfista.profundidadeAtual
    var zonaStatus = ""
    var oxigenioStatus = ""

    if profundidade <= 10 {
        zonaStatus = "🌅 Superfície"
        oxigenioStatus = "✅ O₂ ILIMITADO"
    } else if profundidade <= 50 {
        zonaStatus = "☀️ Águas rasas"
        oxigenioStatus = "🌬️ O₂ Estável"
    } else if profundidade <= 100 {
        zonaStatus = "🌊 Profundidade média"
        oxigenioStatus = "💨 O₂ Limitado"
    } else if profundidade <= 150 {
        zonaStatus = "🌑 Zona profunda"
        oxigenioStatus = "🫧 O₂ CRÍTICO"
    } else {
        zonaStatus = "💀 Zona abissal"
        oxigenioStatus = "⚠️ RISCO DE IMPLOSÃO"
    }

    // Preparar bag de conhecimento para retorno
    var bagArray: [{String: AnyStruct}] = []
    for conhecimento in surfista.bagDeConhecimento {
        bagArray.append({
            "tipo": conhecimento.tipo,
            "descricao": conhecimento.descricao,
            "pontos": conhecimento.pontos,
            "timestamp": conhecimento.timestamp
        })
    }

    return {
        "id": surfista.id,
        "nome": surfista.nome,
        "dataResgate": surfista.dataResgate,
        "profundidadeAtual": profundidade,
        "zonaStatus": zonaStatus,
        "oxigenioStatus": oxigenioStatus,
        "energiaGasta": surfista.energiaGasta,
        "pontosTotal": surfista.pontosTotal,
        "saldoRecompensas": surfista.saldoRecompensas(),
        "conquistas": surfista.conquistas,
        "bagDeConhecimento": bagArray,
        "totalConhecimentos": surfista.bagDeConhecimento.length
    }
}