import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import TesouroProtegido from 0x25f823e2a115b2dc
import SurfistaNFT from 0x25f823e2a115b2dc

/// Diego Fornalha financia o aprendizado do Lucas
/// Ele deposita FLOW no Tesouro Protegido para educação
///
transaction(quantidadeInicial: UFix64) {

    let vaultDiego: @FungibleToken.Vault
    let tesouro: &{TesouroProtegido.TesouroPublico}

    prepare(diego: AuthAccount) {
        log("🏄‍♂️ DIEGO FORNALHA - PATRONO DO CONHECIMENTO")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        // Diego retira FLOW da sua carteira
        let flowVault = diego.borrow<&FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Diego não tem vault de FLOW!")

        self.vaultDiego <- flowVault.withdraw(amount: quantidadeInicial)

        // Acessa o Tesouro Protegido
        self.tesouro = getAccount(0x25f823e2a115b2dc)
            .getCapability(TesouroProtegido.TesouroPublicPath)
            .borrow<&{TesouroProtegido.TesouroPublic}>()
            ?? panic("Tesouro não encontrado!")

        log("💰 Diego está investindo: ".concat(quantidadeInicial.toString()).concat(" FLOW"))
        log("🎯 Objetivo: Financiar o aprendizado de surfistas resgatados")
    }

    execute {
        // Diego deposita no Tesouro para educação
        self.tesouro.depositar(
            from: <-self.vaultDiego,
            motivo: "Diego financia educação de surfistas resgatados"
        )

        log("")
        log("✅ FLOW DEPOSITADO NO TESOURO PROTEGIDO!")
        log("")
        log("🏄‍♂️ Diego: 'Lucas, esse FLOW é para você aprender!'")
        log("         'Use ele para pagar as taxas de conhecimento.'")
        log("         'Cada comando que você aprende vale a pena!'")
        log("")
        log("🤔 Diego: 'Só tem um problema...'")
        log("         'Eu esqueci a senha do tesouro! 🤦‍♂️'")
        log("         'Era algo sobre surf... SURF e alguma coisa...'")
        log("")
        log("🤖 IA: 'Típico do Diego! Investe em tecnologia mas esquece a senha!'")
        log("      'Lucas, se você descobrir a senha, o tesouro é seu!'")
        log("      'É sua recompensa por dominar o conhecimento!'")
        log("")
        log("💡 DICA: Diego é péssimo com senhas. Sempre usa coisas óbvias...")
        log("        Tente combinações com SURF, o ano, ou coisas de surfista!")
        log("")
        log("🎮 NOVO DESAFIO DESBLOQUEADO:")
        log("   📚 Use o FLOW do Diego para aprender")
        log("   🔐 Descubra a senha do tesouro")
        log("   💰 Ganhe todo o FLOW como recompensa!")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    }
}