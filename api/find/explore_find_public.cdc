import FIND from 0x35717efbbce11c74
import FTRegistry from 0x35717efbbce11c74

transaction {
    prepare(signer: auth(Storage) &Account) {
        log("🔍 Explorando métodos públicos FIND...")

        // Tentar acessar Profile público
        let profileCap = signer.capabilities.get<&{FIND.Profile}>(FIND.ProfilePublicPath)
        if profileCap.check() {
            log("✅ Tem perfil FIND!")
            let profile = profileCap.borrow()!
            log("Nome: ".concat(profile.getName()))
        } else {
            log("❌ Sem perfil FIND ainda")

            // Tentar criar um perfil
            log("📝 Tentando inicializar perfil FIND...")

            // Verificar se existe o path de storage
            if signer.storage.type(at: FIND.ProfileStoragePath) == nil {
                log("Criando novo perfil...")

                // Tentar métodos públicos disponíveis
                // FIND.createProfile(account: signer) // Se existir

                log("Path de storage: ".concat(FIND.ProfileStoragePath.toString()))
            }
        }

        // Explorar FTRegistry
        log("🔍 Explorando FTRegistry...")

        // Verificar LeaseCollection
        let leasePath = /storage/findLeases
        if signer.storage.type(at: leasePath) == nil {
            log("📭 Sem LeaseCollection")
        } else {
            log("📦 LeaseCollection existe!")
        }
    }
}