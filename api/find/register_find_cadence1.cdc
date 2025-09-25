import FIND from 0x35717efbbce11c74
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

transaction(name: String, maxAmount: UFix64) {
    let vaultRef: auth(FungibleToken.Withdraw) &FlowToken.Vault
    let leases: &FIND.LeaseCollection
    let cost: UFix64

    prepare(acct: auth(Storage, Capabilities) &Account) {
        // Primeiro, setup inicial se necessário
        if acct.storage.borrow<&FIND.LeaseCollection>(from: FIND.LeaseStoragePath) == nil {
            acct.storage.save(<- FIND.createEmptyLeaseCollection(), to: FIND.LeaseStoragePath)

            // Publicar capability com novo formato Cadence 1.0
            acct.capabilities.unpublish(FIND.LeasePublicPath)
            let cap = acct.capabilities.storage.issue<&FIND.LeaseCollection>(FIND.LeaseStoragePath)
            acct.capabilities.publish(cap, at: FIND.LeasePublicPath)
        }

        // Calcular custo
        self.cost = FIND.calculateCostInFlow(name)

        // Obter referências com novo sistema de storage
        self.vaultRef = acct.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Não foi possível acessar FlowToken vault")

        self.leases = acct.storage.borrow<auth(FIND.LeaseOwner) &FIND.LeaseCollection>(
            from: FIND.LeaseStoragePath
        ) ?? panic("Não foi possível acessar LeaseCollection")
    }

    pre {
        self.cost <= maxAmount : "Valor máximo insuficiente"
        self.vaultRef.balance >= self.cost : "Saldo insuficiente"
    }

    execute {
        let payVault <- self.vaultRef.withdraw(amount: self.cost) as! @FlowToken.Vault
        self.leases.register(name: name, vault: <- payVault)
    }
}