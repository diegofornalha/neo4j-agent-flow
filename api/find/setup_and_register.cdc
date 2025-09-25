import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7
import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FIND from 0x35717efbbce11c74
import Profile from 0x35717efbbce11c74

// Transação combinada: setup + registro
transaction(name: String, maxAmount: UFix64) {

    prepare(account: auth(Storage, Capabilities) &Account) {

        // 1. Setup Profile se necessário
        let profilePath = /storage/findProfile
        let profilePublicPath = /public/findProfile

        if account.storage.borrow<&AnyResource>(from: profilePath) == nil {
            // Criar perfil
            let profile <- Profile.createUser(name: name, createdAt: "find")
            account.storage.save(<-profile, to: profilePath)

            // Publicar capability
            let cap = account.capabilities.storage.issue<&Profile.User>(profilePath)
            account.capabilities.publish(cap, at: profilePublicPath)
        }

        // 2. Setup LeaseCollection se necessário
        if account.storage.borrow<&FIND.LeaseCollection>(from: FIND.LeaseStoragePath) == nil {
            account.storage.save(<- FIND.createEmptyLeaseCollection(), to: FIND.LeaseStoragePath)

            // Publicar capability
            let leaseCap = account.capabilities.storage.issue<&FIND.LeaseCollection>(FIND.LeaseStoragePath)
            account.capabilities.publish(leaseCap, at: FIND.LeasePublicPath)
        }

        // 3. Tentar registrar o nome
        let cost = FIND.calculateCostInFlow(name)

        if cost > maxAmount {
            panic("Custo ".concat(cost.toString()).concat(" maior que máximo permitido ").concat(maxAmount.toString()))
        }

        // Obter vault de Flow
        let vaultRef = account.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Não foi possível acessar FlowToken vault")

        if vaultRef.balance < cost {
            panic("Saldo insuficiente: ".concat(vaultRef.balance.toString()).concat(" < ").concat(cost.toString()))
        }

        // Obter LeaseCollection
        let leases = account.storage.borrow<&FIND.LeaseCollection>(
            from: FIND.LeaseStoragePath
        ) ?? panic("Não foi possível acessar LeaseCollection")

        // Retirar pagamento
        let payVault <- vaultRef.withdraw(amount: cost) as! @FlowToken.Vault

        // Registrar nome
        leases.register(name: name, vault: <- payVault)
    }
}