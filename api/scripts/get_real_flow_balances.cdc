import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7
import FungibleTokenMetadataViews from 0x9a0766d93b6608b7

/// Script para buscar saldo real de FLOW de múltiplos endereços
access(all) fun main(addresses: [Address]): [{String: AnyStruct}] {
    let result: [{String: AnyStruct}] = []
    var rank = 1

    // Lista temporária para ordenação
    let balances: [{String: AnyStruct}] = []

    for address in addresses {
        let account = getAccount(address)

        // Tentar acessar o vault de FLOW
        let vaultRef = account.capabilities
            .get<&{FungibleToken.Balance}>(/public/flowTokenBalance)
            .borrow()

        let balance = vaultRef?.balance ?? 0.0

        balances.append({
            "address": address.toString(),
            "flowBalance": balance,
            "name": address.toString() // Podemos customizar depois
        })
    }

    // Ordenar por saldo (maior primeiro)
    var sorted = balances
    var n = sorted.length

    // Bubble sort simples
    var i = 0
    while i < n - 1 {
        var j = 0
        while j < n - i - 1 {
            let balanceA = sorted[j]["flowBalance"] as! UFix64? ?? 0.0
            let balanceB = sorted[j + 1]["flowBalance"] as! UFix64? ?? 0.0

            if balanceA < balanceB {
                let temp = sorted[j]
                sorted[j] = sorted[j + 1]
                sorted[j + 1] = temp
            }
            j = j + 1
        }
        i = i + 1
    }

    // Adicionar ranking
    for item in sorted {
        result.append({
            "rank": rank,
            "address": item["address"]!,
            "flowBalance": item["flowBalance"]!,
            "name": item["name"]!
        })
        rank = rank + 1
    }

    return result
}