import SurfistaLeaderboard from 0x36395f9dde50ea27

/// Script para buscar o leaderboard de surfistas
access(all) fun main(): [{String: AnyStruct}] {
    let leaderboard = SurfistaLeaderboard.getLeaderboard()

    let result: [{String: AnyStruct}] = []
    var rank = 1

    for surfista in leaderboard {
        result.append({
            "rank": rank,
            "address": surfista.address.toString(),
            "name": surfista.name,
            "flowTokens": surfista.flowTokens,
            "lastUpdated": surfista.lastUpdated
        })
        rank = rank + 1
    }

    return result
}