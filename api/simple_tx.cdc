transaction {
    prepare(signer: auth(Storage) &Account) {
        log("🚀 Transação #2 executada com sucesso!")
        log("📅 Data: 2025-01-25 14:50")
        log("🔑 Assinante: ".concat(signer.address.toString()))
        log("✨ Flow Testnet operacional!")
    }
}