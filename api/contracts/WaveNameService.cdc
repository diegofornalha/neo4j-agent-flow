import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import NonFungibleToken from 0x631e88ae7f1d7c20

/// WaveNameService - Serviço de nomes para o Wave OnFlow Bootcamp
/// Compatível com Cadence 1.0
access(all) contract WaveNameService {

    /// Eventos
    access(all) event NameRegistered(name: String, owner: Address, expiresAt: UFix64)
    access(all) event NameRenewed(name: String, owner: Address, newExpiresAt: UFix64)
    access(all) event NameTransferred(name: String, from: Address, to: Address)
    access(all) event ContractInitialized()

    /// Paths de storage
    access(all) let RegistryStoragePath: StoragePath
    access(all) let RegistryPublicPath: PublicPath
    access(all) let AdminStoragePath: StoragePath

    /// Estrutura de um nome registrado
    access(all) struct NameRecord {
        access(all) let name: String
        access(all) var owner: Address
        access(all) var expiresAt: UFix64
        access(all) var metadata: {String: String}

        init(name: String, owner: Address, expiresAt: UFix64) {
            self.name = name
            self.owner = owner
            self.expiresAt = expiresAt
            self.metadata = {}
        }

        access(all) fun isExpired(): Bool {
            return getCurrentBlock().timestamp > self.expiresAt
        }

        access(contract) fun setOwner(_ newOwner: Address) {
            self.owner = newOwner
        }

        access(contract) fun setExpiry(_ newExpiry: UFix64) {
            self.expiresAt = newExpiry
        }
    }

    /// Registry principal - armazena todos os nomes
    access(all) resource Registry {
        access(self) var names: {String: NameRecord}
        access(self) var reverseNames: {Address: String}

        init() {
            self.names = {}
            self.reverseNames = {}
        }

        /// Registra um novo nome
        access(all) fun register(name: String, owner: Address, duration: UFix64, payment: @FlowToken.Vault) {
            // Verificações manuais sem pre-condições
            if self.names.containsKey(name) {
                let record = self.names[name]!
                if getCurrentBlock().timestamp <= record.expiresAt {
                    panic("Nome já está registrado e não expirou")
                }
            }

            let cost = WaveNameService.calculateCost(name, duration)
            if payment.balance < cost {
                panic("Pagamento insuficiente")
            }

            // Destruir o pagamento (ou transferir para treasury)
            destroy payment

            let expiresAt = getCurrentBlock().timestamp + duration
            let record = NameRecord(name: name, owner: owner, expiresAt: expiresAt)

            self.names[name] = record
            self.reverseNames[owner] = name

            emit NameRegistered(name: name, owner: owner, expiresAt: expiresAt)
        }

        /// Renova um nome existente
        access(all) fun renew(name: String, duration: UFix64, payment: @FlowToken.Vault) {
            // Verificações manuais
            if !self.names.containsKey(name) {
                panic("Nome não existe")
            }

            let cost = WaveNameService.calculateRenewalCost(name, duration)
            if payment.balance < cost {
                panic("Pagamento insuficiente")
            }

            destroy payment

            let record = self.names[name]!
            let newExpiry = record.expiresAt + duration
            record.setExpiry(newExpiry)
            self.names[name] = record

            emit NameRenewed(name: name, owner: record.owner, newExpiresAt: newExpiry)
        }

        /// Transfere um nome para outro endereço
        access(all) fun transfer(name: String, to: Address, from: Address) {
            // Verificações manuais
            if !self.names.containsKey(name) {
                panic("Nome não existe")
            }

            let record = self.names[name]!
            if record.owner != from {
                panic("Apenas o dono pode transferir")
            }

            if record.isExpired() {
                panic("Nome expirado")
            }
            let oldOwner = record.owner

            record.setOwner(to)
            self.names[name] = record

            // Atualizar reverse mapping
            self.reverseNames.remove(key: oldOwner)
            self.reverseNames[to] = name

            emit NameTransferred(name: name, from: oldOwner, to: to)
        }

        /// Verifica se um nome existe
        access(all) fun exists(_ name: String): Bool {
            return self.names.containsKey(name)
        }

        /// Verifica se um nome está expirado
        access(all) fun isExpired(_ name: String): Bool {
            if let record = self.names[name] {
                return record.isExpired()
            }
            return true
        }

        /// Retorna o dono de um nome
        access(all) fun getOwner(_ name: String): Address? {
            if let record = self.names[name] {
                if !record.isExpired() {
                    return record.owner
                }
            }
            return nil
        }

        /// Resolve um nome para um endereço
        access(all) fun resolve(_ name: String): Address? {
            return self.getOwner(name)
        }

        /// Reverse lookup - endereço para nome
        access(all) fun reverseLookup(_ address: Address): String? {
            return self.reverseNames[address]
        }

        /// Retorna informações completas sobre um nome
        access(all) fun getNameInfo(_ name: String): NameRecord? {
            return self.names[name]
        }
    }

    /// Interface pública para o Registry
    access(all) resource interface RegistryPublic {
        access(all) fun resolve(_ name: String): Address?
        access(all) fun reverseLookup(_ address: Address): String?
        access(all) fun exists(_ name: String): Bool
        access(all) fun isExpired(_ name: String): Bool
        access(all) fun getNameInfo(_ name: String): NameRecord?
    }

    /// Admin resource para gerenciar o contrato
    access(all) resource Admin {
        /// Define preço base
        access(all) fun setBasePrice(_ price: UFix64) {
            WaveNameService.basePrice = price
        }
    }

    /// Variáveis do contrato
    access(all) var basePrice: UFix64
    access(all) var totalNames: UInt64

    /// Calcula o custo de registro baseado no comprimento do nome
    access(all) fun calculateCost(_ name: String, _ duration: UFix64): UFix64 {
        let length = name.length
        var multiplier = 1.0

        // Nomes mais curtos são mais caros
        if length <= 3 {
            multiplier = 100.0  // 100 FLOW por ano
        } else if length <= 5 {
            multiplier = 10.0   // 10 FLOW por ano
        } else if length <= 8 {
            multiplier = 5.0    // 5 FLOW por ano
        }
        // Nomes longos: 1 FLOW por ano (multiplier = 1.0)

        let yearlyPrice = self.basePrice * multiplier
        let years = duration / 31536000.0 // segundos em um ano

        return yearlyPrice * years
    }

    /// Calcula o custo de renovação
    access(all) fun calculateRenewalCost(_ name: String, _ duration: UFix64): UFix64 {
        // Renovação tem 20% de desconto
        return self.calculateCost(name, duration) * 0.8
    }

    /// Cria um Registry vazio
    access(all) fun createRegistry(): @Registry {
        return <- create Registry()
    }

    init() {
        // Definir paths
        self.RegistryStoragePath = /storage/waveNameRegistry
        self.RegistryPublicPath = /public/waveNameRegistry
        self.AdminStoragePath = /storage/waveNameAdmin

        // Configurações iniciais
        self.basePrice = 1.0 // 1 FLOW para nomes longos por ano
        self.totalNames = 0

        // Criar e salvar Admin resource
        let admin <- create Admin()
        self.account.storage.save(<-admin, to: self.AdminStoragePath)

        emit ContractInitialized()
    }
}