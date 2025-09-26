import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Contrato de Leaderboard para Surfistas baseado em FLOW tokens
access(all) contract SurfistaLeaderboard {

    /// Evento emitido quando um surfista é adicionado ou atualizado
    access(all) event SurfistaUpdated(address: Address, name: String, flowTokens: UFix64)

    /// Evento emitido quando tokens são depositados
    access(all) event TokensDeposited(address: Address, amount: UFix64)

    /// Estrutura para armazenar dados do surfista
    access(all) struct SurfistaData {
        access(all) let address: Address
        access(all) var name: String
        access(all) var flowTokens: UFix64
        access(all) var lastUpdated: UFix64

        init(address: Address, name: String, flowTokens: UFix64) {
            self.address = address
            self.name = name
            self.flowTokens = flowTokens
            self.lastUpdated = getCurrentBlock().timestamp
        }

        access(all) fun updateTokens(_ amount: UFix64) {
            self.flowTokens = self.flowTokens + amount
            self.lastUpdated = getCurrentBlock().timestamp
        }
    }

    /// Armazena todos os surfistas
    access(self) let surfistas: {Address: SurfistaData}

    /// Vault para receber FLOW tokens
    access(self) let vault: @FlowToken.Vault

    /// Path para o Admin
    access(all) let AdminStoragePath: StoragePath

    /// Resource Admin para gerenciar o leaderboard
    access(all) resource Admin {

        /// Adiciona ou atualiza um surfista
        access(all) fun addOrUpdateSurfista(address: Address, name: String, flowTokens: UFix64) {
            if let existing = SurfistaLeaderboard.surfistas[address] {
                // Atualizar existente
                existing.updateTokens(flowTokens)
                SurfistaLeaderboard.surfistas[address] = existing
            } else {
                // Adicionar novo
                let surfista = SurfistaData(
                    address: address,
                    name: name.length > 0 ? name : address.toString(),
                    flowTokens: flowTokens
                )
                SurfistaLeaderboard.surfistas[address] = surfista
            }

            emit SurfistaUpdated(
                address: address,
                name: SurfistaLeaderboard.surfistas[address]?.name ?? "",
                flowTokens: SurfistaLeaderboard.surfistas[address]?.flowTokens ?? 0.0
            )
        }

        /// Remove um surfista
        access(all) fun removeSurfista(address: Address) {
            SurfistaLeaderboard.surfistas.remove(key: address)
        }

        /// Limpa todo o leaderboard
        access(all) fun clearLeaderboard() {
            for key in SurfistaLeaderboard.surfistas.keys {
                SurfistaLeaderboard.surfistas.remove(key: key)
            }
        }
    }

    /// Função pública para depositar tokens e atualizar score
    access(all) fun depositTokens(from: Address, vault: @{FungibleToken.Vault}) {
        let amount = vault.balance

        // Depositar no vault do contrato
        SurfistaLeaderboard.vault.deposit(from: <-vault)

        // Atualizar ou adicionar surfista
        if let existing = self.surfistas[from] {
            existing.updateTokens(amount)
            self.surfistas[from] = existing
        } else {
            let surfista = SurfistaData(
                address: from,
                name: from.toString(),
                flowTokens: amount
            )
            self.surfistas[from] = surfista
        }

        emit TokensDeposited(address: from, amount: amount)
        emit SurfistaUpdated(
            address: from,
            name: self.surfistas[from]?.name ?? "",
            flowTokens: self.surfistas[from]?.flowTokens ?? 0.0
        )
    }

    /// Retorna o leaderboard ordenado
    access(all) fun getLeaderboard(): [SurfistaData] {
        let surfistasList: [SurfistaData] = []

        for address in self.surfistas.keys {
            if let surfista = self.surfistas[address] {
                surfistasList.append(surfista)
            }
        }

        // Ordenar por flowTokens (maior primeiro)
        var sorted = surfistasList
        var n = sorted.length

        // Bubble sort simples
        var i = 0
        while i < n - 1 {
            var j = 0
            while j < n - i - 1 {
                if sorted[j].flowTokens < sorted[j + 1].flowTokens {
                    let temp = sorted[j]
                    sorted[j] = sorted[j + 1]
                    sorted[j + 1] = temp
                }
                j = j + 1
            }
            i = i + 1
        }

        return sorted
    }

    /// Retorna dados de um surfista específico
    access(all) fun getSurfista(address: Address): SurfistaData? {
        return self.surfistas[address]
    }

    /// Retorna o total de surfistas
    access(all) fun getTotalSurfistas(): Int {
        return self.surfistas.length
    }

    /// Retorna o total de FLOW tokens no vault
    access(all) fun getTotalTokens(): UFix64 {
        return self.vault.balance
    }

    /// Cria um Admin resource
    access(all) fun createAdmin(): @Admin {
        return <-create Admin()
    }

    init() {
        self.surfistas = {}
        self.vault <- FlowToken.createEmptyVault(vaultType: Type<@FlowToken.Vault>()) as! @FlowToken.Vault

        self.AdminStoragePath = /storage/SurfistaLeaderboardAdmin

        // Salvar Admin na conta que faz o deploy
        let admin <- create Admin()
        self.account.storage.save(<-admin, to: self.AdminStoragePath)
    }
}