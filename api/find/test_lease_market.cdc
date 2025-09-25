import FIND from 0x35717efbbce11c74
import FindLeaseMarket from 0x35717efbbce11c74
import FindLeaseMarketSale from 0x35717efbbce11c74
import FungibleToken from 0x9a0766d93b6608b7

transaction {
    prepare(signer: auth(Storage) &Account) {
        log("🔍 Testando FindLeaseMarket...")
        log("📍 Conta: ".concat(signer.address.toString()))

        // Verificar se existe uma coleção de lease
        let leasePath = /storage/findLeases
        let leasePublicPath = /public/findLeases

        if signer.storage.type(at: leasePath) == nil {
            log("📭 Sem coleção de leases ainda")

            // Tentar criar/inicializar uma coleção
            log("💡 Verificando se há métodos públicos de inicialização...")

            // Verificar paths de mercado
            let marketPath = /storage/findLeaseMarket
            if signer.storage.type(at: marketPath) == nil {
                log("📭 Sem mercado de leases")
            } else {
                log("📦 Mercado de leases existe!")
            }

        } else {
            log("📦 Coleção de leases existe!")

            // Tentar listar leases
            log("📋 Tentando acessar leases...")
        }

        // Verificar FungibleToken vault
        let vaultPath = /storage/flowTokenVault
        if signer.storage.type(at: vaultPath) != nil {
            log("💰 Vault de Flow Token encontrado!")
        }

        // Tentar acessar informações públicas do FIND
        log("🔍 Explorando informações públicas...")

        // Verificar se existem capabilities públicas
        let pubPath = /public/findPack
        if signer.capabilities.exists(pubPath) {
            log("📦 Capability findPack existe!")
        }

    }
}