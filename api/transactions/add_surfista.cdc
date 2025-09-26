import SurfistaLeaderboard from 0x36395f9dde50ea27

/// Transação para adicionar ou atualizar um surfista (requer Admin)
transaction(surfistaAddress: Address, name: String, flowTokens: UFix64) {

    let admin: &SurfistaLeaderboard.Admin

    prepare(signer: auth(Storage) &Account) {
        // Pegar referência do Admin
        self.admin = signer.storage.borrow<&SurfistaLeaderboard.Admin>(
            from: SurfistaLeaderboard.AdminStoragePath
        ) ?? panic("Admin não encontrado. Apenas o deployer pode adicionar surfistas.")
    }

    execute {
        self.admin.addOrUpdateSurfista(
            address: surfistaAddress,
            name: name,
            flowTokens: flowTokens
        )

        log("✅ Surfista adicionado/atualizado:")
        log("📍 Endereço: ".concat(surfistaAddress.toString()))
        log("🏄 Nome: ".concat(name))
        log("💰 FLOW Tokens: ".concat(flowTokens.toString()))
    }
}