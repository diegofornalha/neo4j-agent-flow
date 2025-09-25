import FTRegistry from 0x35717efbbce11c74
import FIND from 0x35717efbbce11c74
import FindMarket from 0x35717efbbce11c74
import FindMarketSale from 0x35717efbbce11c74
import FindLeaseMarket from 0x35717efbbce11c74
import FindLeaseMarketSale from 0x35717efbbce11c74

transaction {
    prepare(signer: auth(Storage) &Account) {
        log("✅ Todos os imports funcionaram!")
        log("📍 Conta: ".concat(signer.address.toString()))

        // Testar se conseguimos acessar FTRegistry
        log("🔍 Testando acesso ao FTRegistry...")

        // Verificar se temos alguma coleção FIND
        let findPath = /storage/findLeases
        if signer.storage.type(at: findPath) != nil {
            log("📦 Encontrou coleção FIND em storage!")
        } else {
            log("📭 Nenhuma coleção FIND ainda")
        }

        // Verificar públicos
        let publicPath = /public/findLeases
        if signer.capabilities.exists(publicPath) {
            log("🔓 Capability pública existe!")
        }
    }
}