import WaveNameService from 0x36395f9dde50ea27

/// Setup inicial - cria o Registry para a conta
transaction {
    prepare(account: auth(Storage, Capabilities) &Account) {
        // Verificar se já existe
        if account.storage.type(at: WaveNameService.RegistryStoragePath) != nil {
            log("Registry já existe")
            return
        }

        // Criar e salvar Registry
        let registry <- WaveNameService.createRegistry()
        account.storage.save(<-registry, to: WaveNameService.RegistryStoragePath)

        // Publicar capability
        let cap = account.capabilities.storage.issue<&WaveNameService.Registry>(
            WaveNameService.RegistryStoragePath
        )
        account.capabilities.publish(cap, at: WaveNameService.RegistryPublicPath)

        log("✅ WaveNameService Registry criado com sucesso!")
    }
}