import TesouroProtegido from 0x25f823e2a115b2dc
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// Transaction para tentar sacar fundos do Tesouro Protegido
/// Precisa da senha correta!
///
transaction(senha: String, quantidade: UFix64) {

    let tesouro: &{TesouroProtegido.TesouroPublico}
    let receptor: &{FungibleToken.Receiver}

    prepare(signer: AuthAccount) {
        // Obter referência do tesouro
        self.tesouro = getAccount(0x25f823e2a115b2dc)
            .getCapability(TesouroProtegido.TesouroPublicPath)
            .borrow<&{TesouroProtegido.TesouroPublico}>()
            ?? panic("Não foi possível acessar o Tesouro Protegido")

        // Preparar receptor (vault do usuário)
        self.receptor = signer
            .getCapability(/public/flowTokenReceiver)
            .borrow<&{FungibleToken.Receiver}>()
            ?? panic("Não foi possível acessar o receptor de FLOW")
    }

    execute {
        log("🔐 TENTANDO ABRIR O TESOURO PROTEGIDO...")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log("🔑 Senha fornecida: ****** (ocultada)")
        log("💰 Quantidade solicitada: ".concat(quantidade.toString()).concat(" FLOW"))
        log("")

        let sucesso = self.tesouro.tentarSacar(
            senha: senha,
            amount: quantidade,
            receptor: self.receptor
        )

        if sucesso {
            log("✅ SUCESSO! TESOURO ABERTO!")
            log("🎊 Você descobriu a senha!")
            log("💰 ".concat(quantidade.toString()).concat(" FLOW transferidos para sua conta!"))
            log("")
            log("🏄 Diego: 'Cara, como você descobriu a senha?!'")
            log("🤖 IA: 'Parabéns! Você é um verdadeiro hacker do bem!'")
        } else {
            log("❌ ACESSO NEGADO!")
            log("🔒 Senha incorreta ou saldo insuficiente!")
            log("")

            // Tentar obter dica
            if let dica = self.tesouro.obterDica() {
                log("💡 DICA: ".concat(dica))
            } else {
                log("💡 Continue tentando para revelar dicas...")
            }

            log("")
            log("🏄 Diego: 'Eu também não lembro a senha...'")
            log("🤖 IA: 'Tente pensar em algo relacionado ao Diego e surf!'")
        }

        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    }
}