import SurfistaLeaderboard from 0x36395f9dde50ea27

/// Configurar leaderboard com os participantes reais da testnet
transaction {
    let admin: &SurfistaLeaderboard.Admin

    prepare(signer: auth(Storage) &Account) {
        self.admin = signer.storage.borrow<&SurfistaLeaderboard.Admin>(
            from: SurfistaLeaderboard.AdminStoragePath
        ) ?? panic("Admin não encontrado")
    }

    execute {
        // Limpar leaderboard atual
        self.admin.clearLeaderboard()

        // Adicionar os 4 participantes reais das submissions
        self.admin.addOrUpdateSurfista(address: 0xaf074399a1d7fe55, name: "Surfista #1", flowTokens: 25.0)
        self.admin.addOrUpdateSurfista(address: 0x962c63b2b3b15a8b, name: "Surfista #2", flowTokens: 20.0)
        self.admin.addOrUpdateSurfista(address: 0x8b9a5d24cb3b0164, name: "Surfista #3", flowTokens: 15.0)
        self.admin.addOrUpdateSurfista(address: 0xad5a851aeb126bca, name: "Surfista #4", flowTokens: 10.0)

        log("✅ Leaderboard configurado com participantes reais da testnet!")
        log("🥇 0xaf074399a1d7fe55 - 25.0 FLOW")
        log("🥈 0x962c63b2b3b15a8b - 20.0 FLOW")
        log("🥉 0x8b9a5d24cb3b0164 - 15.0 FLOW")
        log("4º 0xad5a851aeb126bca - 10.0 FLOW")
    }
}