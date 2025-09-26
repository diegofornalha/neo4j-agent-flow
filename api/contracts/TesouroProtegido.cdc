import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// TesouroProtegido - Cofre do submarino que armazena todos os FLOW pagos
/// Apenas quem conhece a senha pode retirar os fundos
/// Todas as taxas de conhecimento e presentes vão para cá
///
access(all) contract TesouroProtegido {

    /// Eventos
    access(all) event DepositoNoTesouro(amount: UFix64, from: Address?, motivo: String)
    access(all) event TentativaAcesso(sucesso: Bool, address: Address?)
    access(all) event RetiradaDoTesouro(amount: UFix64, to: Address?)
    access(all) event SenhaAlterada(por: Address?)
    access(all) event DicaRevelada(dica: String)

    /// Caminho do cofre
    access(all) let TesouroStoragePath: StoragePath
    access(all) let TesouroPublicPath: PublicPath
    access(all) let AdminStoragePath: StoragePath

    /// Hash da senha (não armazenamos a senha em texto claro)
    access(self) var senhaHash: String

    /// Contador de tentativas falhas
    access(all) var tentativasFalhas: UInt64

    /// Dicas progressivas (reveladas após X tentativas falhas)
    access(self) let dicas: [String]

    /// Interface pública do Tesouro
    access(all) resource interface TesouroPublico {
        /// Qualquer um pode depositar FLOW no tesouro
        access(all) fun depositar(from: @FungibleToken.Vault, motivo: String)

        /// Ver saldo do tesouro (público)
        access(all) fun verSaldo(): UFix64

        /// Tentar sacar com senha
        access(all) fun tentarSacar(senha: String, amount: UFix64, receptor: &{FungibleToken.Receiver}): Bool

        /// Obter dica (após muitas tentativas falhas)
        access(all) fun obterDica(): String?

        /// Ver histórico de depósitos
        access(all) fun verHistorico(): [DepositoInfo]
    }

    /// Estrutura para armazenar informações de depósito
    access(all) struct DepositoInfo {
        access(all) let amount: UFix64
        access(all) let motivo: String
        access(all) let timestamp: UFix64

        init(amount: UFix64, motivo: String) {
            self.amount = amount
            self.motivo = motivo
            self.timestamp = getCurrentBlock().timestamp
        }
    }

    /// Resource do Tesouro Protegido
    access(all) resource Tesouro: TesouroPublico {
        /// Vault que armazena todo o FLOW
        access(self) let vault: @FlowToken.Vault

        /// Histórico de todos os depósitos
        access(self) let historico: [DepositoInfo]

        init() {
            self.vault <- FlowToken.createEmptyVault() as! @FlowToken.Vault
            self.historico = []
        }

        /// Depositar FLOW no tesouro (qualquer um pode depositar)
        access(all) fun depositar(from: @FungibleToken.Vault, motivo: String) {
            let amount = from.balance
            self.vault.deposit(from: <-from)

            // Registrar no histórico
            self.historico.append(DepositoInfo(
                amount: amount,
                motivo: motivo
            ))

            emit DepositoNoTesouro(amount: amount, from: self.owner?.address, motivo: motivo)
        }

        /// Ver saldo atual do tesouro
        access(all) fun verSaldo(): UFix64 {
            return self.vault.balance
        }

        /// Ver histórico de depósitos
        access(all) fun verHistorico(): [DepositoInfo] {
            return self.historico
        }

        /// Tentar sacar fundos com senha
        access(all) fun tentarSacar(senha: String, amount: UFix64, receptor: &{FungibleToken.Receiver}): Bool {
            // Verificar senha (simplificado - em produção usar hash seguro)
            if self.verificarSenha(senha) {
                // Senha correta! Liberar fundos
                if amount <= self.vault.balance {
                    let fundos <- self.vault.withdraw(amount: amount)
                    receptor.deposit(from: <-fundos)

                    emit RetiradaDoTesouro(amount: amount, to: receptor.owner?.address)
                    emit TentativaAcesso(sucesso: true, address: receptor.owner?.address)

                    // Reset contador de tentativas
                    TesouroProtegido.tentativasFalhas = 0

                    return true
                }
            } else {
                // Senha incorreta
                TesouroProtegido.tentativasFalhas = TesouroProtegido.tentativasFalhas + 1
                emit TentativaAcesso(sucesso: false, address: receptor.owner?.address)
            }

            return false
        }

        /// Verificar se a senha está correta
        access(self) fun verificarSenha(_ senha: String): Bool {
            // Simplificado - em produção usar bcrypt ou similar
            return self.hashSenha(senha) == TesouroProtegido.senhaHash
        }

        /// Hash simples da senha (em produção usar algo mais seguro)
        access(self) fun hashSenha(_ senha: String): String {
            // Placeholder - implementar hash real
            return senha.concat("_hash_submarino")
        }

        /// Obter dica baseada no número de tentativas
        access(all) fun obterDica(): String? {
            let tentativas = TesouroProtegido.tentativasFalhas

            if tentativas >= 50 {
                emit DicaRevelada(dica: TesouroProtegido.dicas[2])
                return TesouroProtegido.dicas[2]  // Dica completa
            } else if tentativas >= 25 {
                emit DicaRevelada(dica: TesouroProtegido.dicas[1])
                return TesouroProtegido.dicas[1]  // Dica média
            } else if tentativas >= 10 {
                emit DicaRevelada(dica: TesouroProtegido.dicas[0])
                return TesouroProtegido.dicas[0]  // Dica inicial
            }

            return nil
        }

        destroy() {
            destroy self.vault
        }
    }

    /// Criar um novo Tesouro vazio
    access(all) fun criarTesouro(): @Tesouro {
        return <- create Tesouro()
    }

    /// Admin resource para gerenciar o tesouro
    access(all) resource Admin {
        /// Alterar a senha do tesouro
        access(all) fun alterarSenha(novaSenha: String) {
            TesouroProtegido.senhaHash = novaSenha.concat("_hash_submarino")
            emit SenhaAlterada(por: self.owner?.address)
        }

        /// Adicionar nova dica
        access(all) fun adicionarDica(dica: String) {
            TesouroProtegido.dicas.append(dica)
        }
    }

    init() {
        self.TesouroStoragePath = /storage/tesouroProtegido
        self.TesouroPublicPath = /public/tesouroProtegido
        self.AdminStoragePath = /storage/tesouroAdmin

        // Senha inicial do submarino (Diego esqueceu de mudar)
        self.senhaHash = "SURF2024_hash_submarino"

        self.tentativasFalhas = 0

        // Dicas progressivas sobre a senha
        self.dicas = [
            "A senha tem a ver com surf e o ano atual...",
            "Começa com SURF e tem 4 dígitos...",
            "SURF + ano que Diego comprou o submarino (2024)"
        ]

        // Criar e salvar o tesouro
        let tesouro <- create Tesouro()
        self.account.save(<-tesouro, to: self.TesouroStoragePath)

        // Publicar interface pública
        self.account.link<&Tesouro{TesouroPublico}>(
            self.TesouroPublicPath,
            target: self.TesouroStoragePath
        )

        // Criar e salvar admin
        let admin <- create Admin()
        self.account.save(<-admin, to: self.AdminStoragePath)
    }
}