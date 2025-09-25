import FlowToken from 0x7e60df042a9c0868
import FIND from 0x35717efbbce11c74
import FungibleToken from 0x9a0766d93b6608b7

transaction(name: String, maxAmount: UFix64) {

    let vaultRef : auth(FungibleToken.Withdraw) &FlowToken.Vault?
    let leases : auth(FIND.LeaseOwner) &FIND.LeaseCollection?
    let cost : UFix64

    prepare(account: auth(BorrowValue, SaveValue, IssueStorageCapabilityController, PublishCapability) &Account) {

        // Setup LeaseCollection se necessário
        let leaseCollection = account.capabilities.get<&FIND.LeaseCollection>(FIND.LeasePublicPath)
        if !leaseCollection.check() {
            account.storage.save(<- FIND.createEmptyLeaseCollection(), to: FIND.LeaseStoragePath)
            let cap = account.capabilities.storage.issue<&FIND.LeaseCollection>(FIND.LeaseStoragePath)
            account.capabilities.publish(cap, at: FIND.LeasePublicPath)
        }

        self.vaultRef = account.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
        self.leases = account.storage.borrow<auth(FIND.LeaseOwner) &FIND.LeaseCollection>(from: FIND.LeaseStoragePath)

        self.cost = FIND.calculateCostInFlow(name)
    }

    pre{
        self.cost <= maxAmount : "Custo maior que máximo: ".concat(self.cost.toString())
        self.vaultRef != nil : "Vault não encontrado!"
        self.leases != nil : "LeaseCollection não encontrado!"
        self.vaultRef!.balance > self.cost : "Saldo insuficiente: ".concat(self.vaultRef!.balance.toString())
    }

    execute{
        let payVault <- self.vaultRef!.withdraw(amount: self.cost) as! @FlowToken.Vault
        self.leases!.register(name: name, vault: <- payVault)
    }
}