import SurfistaLeaderboard from 0x36395f9dde50ea27

/// Adicionar os 3 participantes restantes ao leaderboard
transaction {
    let admin: &SurfistaLeaderboard.Admin

    prepare(signer: auth(Storage) &Account) {
        self.admin = signer.storage.borrow<&SurfistaLeaderboard.Admin>(
            from: SurfistaLeaderboard.AdminStoragePath
        ) ?? panic("Admin não encontrado")
    }

    execute {
        // Adicionar os 3 participantes que faltam
        self.admin.addOrUpdateSurfista(address: 0x94b619cc671a3734, name: "Sexto Lugar", flowTokens: 3.0)
        self.admin.addOrUpdateSurfista(address: 0x9f7145728ef9ae10, name: "Sétimo Lugar", flowTokens: 2.0)
        self.admin.addOrUpdateSurfista(address: 0xcbcf825ca81dcadc, name: "Oitavo Lugar", flowTokens: 1.0)

        log("✅ Participantes adicionados ao leaderboard!")
        log("6º 0x94b619cc671a3734 - 3.0 FLOW")
        log("7º 0x9f7145728ef9ae10 - 2.0 FLOW")
        log("8º 0xcbcf825ca81dcadc - 1.0 FLOW")
    }
}