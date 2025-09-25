import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7
import WaveNameService from 0x36395f9dde50ea27

/// Registra um nome no WaveNameService
transaction(name: String, years: UFix64) {

    let registry: &WaveNameService.Registry
    let vault: auth(FungibleToken.Withdraw) &FlowToken.Vault
    let address: Address

    prepare(account: auth(Storage) &Account) {
        // Obter registry
        self.registry = account.storage.borrow<&WaveNameService.Registry>(
            from: WaveNameService.RegistryStoragePath
        ) ?? panic("Registry não encontrado. Execute setup_wave_registry primeiro!")

        // Obter vault
        self.vault = account.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Flow Token vault não encontrado")

        self.address = account.address
    }

    execute {
        // Calcular duração em segundos
        let duration = years * 31536000.0 // segundos em um ano

        // Calcular custo
        let cost = WaveNameService.calculateCost(name, duration)

        log("📝 Registrando nome: ".concat(name))
        log("⏱️ Duração: ".concat(years.toString()).concat(" anos"))
        log("💰 Custo: ".concat(cost.toString()).concat(" FLOW"))

        // Retirar pagamento
        let payment <- self.vault.withdraw(amount: cost) as! @FlowToken.Vault

        // Registrar nome
        self.registry.register(
            name: name,
            owner: self.address,
            duration: duration,
            payment: <- payment
        )

        log("✅ Nome '".concat(name).concat("' registrado com sucesso!"))
        log("👤 Proprietário: ".concat(self.address.toString()))
    }
}