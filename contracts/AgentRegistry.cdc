// AgentRegistry.cdc - Smart Contract para Registro de Agentes na Flow
// Este contrato gerencia o registro e coordenação de agentes inteligentes

pub contract AgentRegistry {

    // Eventos emitidos pelo contrato
    pub event AgentRegistered(id: UInt64, address: Address, name: String, type: String)
    pub event AgentActionExecuted(agentId: UInt64, action: String, timestamp: UFix64)
    pub event RewardDistributed(agentId: UInt64, amount: UFix64)

    // Paths de armazenamento
    pub let AgentStoragePath: StoragePath
    pub let AgentPublicPath: PublicPath
    pub let AdminStoragePath: StoragePath

    // Contador de agentes registrados
    pub var totalAgents: UInt64

    // Estrutura de dados de um agente
    pub struct AgentData {
        pub let id: UInt64
        pub let owner: Address
        pub let name: String
        pub let agentType: String
        pub let registrationTime: UFix64
        pub var reputation: UFix64
        pub var actionsExecuted: UInt64
        pub var totalRewards: UFix64
        pub var isActive: Bool
        pub var metadata: {String: String}

        init(
            id: UInt64,
            owner: Address,
            name: String,
            agentType: String
        ) {
            self.id = id
            self.owner = owner
            self.name = name
            self.agentType = agentType
            self.registrationTime = getCurrentBlock().timestamp
            self.reputation = 100.0  // Reputação inicial
            self.actionsExecuted = 0
            self.totalRewards = 0.0
            self.isActive = true
            self.metadata = {}
        }

        // Atualiza reputação do agente
        pub fun updateReputation(_ delta: Fix64) {
            let newRep = Fix64(self.reputation) + delta
            if newRep >= 0.0 {
                self.reputation = UFix64(newRep)
            } else {
                self.reputation = 0.0
            }
        }

        // Registra execução de ação
        pub fun recordAction() {
            self.actionsExecuted = self.actionsExecuted + 1
        }

        // Adiciona recompensa
        pub fun addReward(_ amount: UFix64) {
            self.totalRewards = self.totalRewards + amount
        }
    }

    // Interface pública para agentes
    pub resource interface AgentPublic {
        pub fun getAgentData(): AgentData
        pub fun getReputation(): UFix64
        pub fun getActionsCount(): UInt64
        pub fun isActive(): Bool
    }

    // Recurso do Agente
    pub resource Agent: AgentPublic {
        pub var data: AgentData

        init(name: String, agentType: String, owner: Address) {
            AgentRegistry.totalAgents = AgentRegistry.totalAgents + 1
            self.data = AgentData(
                id: AgentRegistry.totalAgents,
                owner: owner,
                name: name,
                agentType: agentType
            )
        }

        pub fun getAgentData(): AgentData {
            return self.data
        }

        pub fun getReputation(): UFix64 {
            return self.data.reputation
        }

        pub fun getActionsCount(): UInt64 {
            return self.data.actionsExecuted
        }

        pub fun isActive(): Bool {
            return self.data.isActive
        }

        // Executa uma ação (apenas owner)
        pub fun executeAction(action: String) {
            pre {
                self.data.isActive: "Agent must be active"
            }

            self.data.recordAction()

            emit AgentActionExecuted(
                agentId: self.data.id,
                action: action,
                timestamp: getCurrentBlock().timestamp
            )
        }

        // Atualiza metadados (apenas owner)
        pub fun updateMetadata(key: String, value: String) {
            self.data.metadata[key] = value
        }

        // Desativa o agente (apenas owner)
        pub fun deactivate() {
            self.data.isActive = false
        }

        // Reativa o agente (apenas owner)
        pub fun reactivate() {
            self.data.isActive = true
        }
    }

    // Interface do Admin
    pub resource interface AdminPublic {
        pub fun getTotalAgents(): UInt64
    }

    // Recurso Admin para gerenciar o registro
    pub resource Admin: AdminPublic {

        pub fun getTotalAgents(): UInt64 {
            return AgentRegistry.totalAgents
        }

        // Cria um novo agente
        pub fun createAgent(
            name: String,
            agentType: String,
            owner: Address
        ): @Agent {
            let agent <- create Agent(
                name: name,
                agentType: agentType,
                owner: owner
            )

            emit AgentRegistered(
                id: agent.data.id,
                address: owner,
                name: name,
                type: agentType
            )

            return <- agent
        }

        // Distribui recompensa para agente
        pub fun distributeReward(
            agentCap: &Agent,
            amount: UFix64,
            reason: String
        ) {
            agentCap.data.addReward(amount)

            // Aumenta reputação baseado na recompensa
            let repIncrease = amount / 100.0
            agentCap.data.updateReputation(Fix64(repIncrease))

            emit RewardDistributed(
                agentId: agentCap.data.id,
                amount: amount
            )
        }

        // Penaliza agente por má conduta
        pub fun penalizeAgent(
            agentCap: &Agent,
            penalty: UFix64,
            reason: String
        ) {
            agentCap.data.updateReputation(-Fix64(penalty))

            // Se reputação muito baixa, desativa
            if agentCap.data.reputation < 10.0 {
                agentCap.deactivate()
            }
        }
    }

    // Função para criar um admin (apenas na inicialização)
    pub fun createAdmin(): @Admin {
        return <- create Admin()
    }

    // Inicialização do contrato
    init() {
        self.totalAgents = 0

        self.AgentStoragePath = /storage/AgentRegistry
        self.AgentPublicPath = /public/AgentRegistry
        self.AdminStoragePath = /storage/AgentRegistryAdmin

        // Cria e salva o admin
        let admin <- create Admin()
        self.account.save(<- admin, to: self.AdminStoragePath)
    }
}