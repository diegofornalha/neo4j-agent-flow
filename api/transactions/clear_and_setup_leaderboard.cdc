import SurfistaLeaderboard from 0x36395f9dde50ea27

/// Limpar e configurar o leaderboard com os surfistas corretos
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

        // Adicionar os 5 surfistas com seus tokens
        self.admin.addOrUpdateSurfista(address: 0x1dcdc8409a2a1cfa, name: "Primeiro Lugar", flowTokens: 25.0)
        self.admin.addOrUpdateSurfista(address: 0xaf074399a1d7fe55, name: "Segundo Lugar", flowTokens: 20.0)
        self.admin.addOrUpdateSurfista(address: 0x962c63b2b3b15a8b, name: "Terceiro Lugar", flowTokens: 15.0)
        self.admin.addOrUpdateSurfista(address: 0x0012a1ef98accd88, name: "Quarto Lugar", flowTokens: 10.0)
        self.admin.addOrUpdateSurfista(address: 0x8b9a5d24cb3b0164, name: "Quinto Lugar", flowTokens: 5.0)

        log("✅ Leaderboard configurado com sucesso!")
        log("🥇 0x1dcdc8409a2a1cfa - 25.0 FLOW")
        log("🥈 0xaf074399a1d7fe55 - 20.0 FLOW")
        log("🥉 0x962c63b2b3b15a8b - 15.0 FLOW")
        log("4º 0x0012a1ef98accd88 - 10.0 FLOW")
        log("5º 0x8b9a5d24cb3b0164 - 5.0 FLOW")
    }
}