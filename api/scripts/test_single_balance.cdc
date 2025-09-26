import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

access(all) fun main(addr: Address): UFix64 {
    let account = getAccount(addr)
    let vaultRef = account.capabilities
        .get<&{FungibleToken.Balance}>(/public/flowTokenBalance)
        .borrow()

    return vaultRef?.balance ?? 0.0
}