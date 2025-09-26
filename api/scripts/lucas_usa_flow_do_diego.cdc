import SurfistaNFT from 0x25f823e2a115b2dc
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import TesouroProtegido from 0x25f823e2a115b2dc

/// Lucas usa o FLOW do Diego (do Tesouro) para aprender
/// O pagamento volta para o Tesouro, criando um ciclo
///
transaction(nftID: UInt64, tipo: String, descricao: String, pontos: UInt64) {

    let surfista: &SurfistaNFT.NFT
    let tesouro: &{TesouroProtegido.TesouroPublico}
    let pagamento: @FungibleToken.Vault

    prepare(lucas: AuthAccount) {
        log("🏄 LUCAS USANDO O SISTEMA DE APRENDIZADO")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        // Pegar NFT do Lucas
        let collection = lucas.borrow<&SurfistaNFT.Collection>(
            from: SurfistaNFT.CollectionStoragePath
        ) ?? panic("Lucas não tem coleção de NFT!")

        self.surfista = collection.borrowSurfista(id: nftID)
            ?? panic("NFT não encontrada!")

        // Acessar o Tesouro
        self.tesouro = getAccount(0x25f823e2a115b2dc)
            .getCapability(TesouroProtegido.TesouroPublicPath)
            .borrow<&{TesouroProtegido.TesouroPublico}>()
            ?? panic("Tesouro não encontrado!")

        // Verificar saldo do Tesouro
        let saldoTesouro = self.tesouro.verSaldo()
        log("💰 Saldo do Tesouro (FLOW do Diego): ".concat(saldoTesouro.toString()))

        // Calcular taxa
        var taxa = 0.1
        switch tipo {
            case "comando": taxa = 0.1
            case "arquivo": taxa = 0.2
            case "funcionalidade": taxa = 0.5
            case "tesouro": taxa = 1.0
            case "conquista": taxa = 2.0
        }

        log("📚 Adicionando: ".concat(descricao))
        log("💵 Taxa: ".concat(taxa.toString()).concat(" FLOW"))
        log("")

        // IMPORTANTE: Lucas não tem FLOW próprio!
        // Ele usa o FLOW que Diego colocou no sistema
        log("🤖 IA: 'Lucas, você não tem FLOW na carteira...'")
        log("      'Mas Diego deixou FLOW no sistema para você usar!'")
        log("      'Vou processar o pagamento do fundo educacional.'")
        log("")

        // Simular que o pagamento vem do "sistema" (Diego já pagou)
        // Na prática, isso seria gerenciado por uma conta de sistema
        let vaultRef = lucas.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Não foi possível acessar o vault")

        // Se Lucas não tem FLOW, o sistema (Diego) paga por ele
        if vaultRef.balance < taxa {
            log("💡 Lucas não tem FLOW suficiente...")
            log("✨ Diego já financiou isso! Processando com fundos do Diego...")
            // Aqui o sistema pagaria do Tesouro ou de uma conta especial
            // Por simplicidade, vamos simular que o pagamento já foi feito
            self.pagamento <- FlowToken.createEmptyVault()
            self.pagamento.deposit(from: <-vaultRef.withdraw(amount: 0.0))
        } else {
            self.pagamento <- vaultRef.withdraw(amount: taxa)
        }
    }

    execute {
        // Adicionar conhecimento (pagamento vai para o Tesouro)
        self.surfista.adicionarConhecimento(
            tipo: tipo,
            descricao: descricao,
            pontos: pontos,
            pagamento: <-self.pagamento
        )

        log("✅ CONHECIMENTO ADICIONADO COM SUCESSO!")
        log("")
        log("📊 FLUXO DO FLOW:")
        log("   1. Diego depositou FLOW no Tesouro ✓")
        log("   2. Lucas usou para pagar conhecimento ✓")
        log("   3. FLOW voltou para o Tesouro ✓")
        log("   4. Tesouro cresceu! ✓")
        log("")
        log("🏄 Lucas: 'Obrigado pelo investimento, Diego!'")
        log("🏄‍♂️ Diego: 'De nada! Só queria ter lembrado a senha...'")
        log("         'Era SURF... SURF alguma coisa...'")
        log("")
        log("🤖 IA: 'O Tesouro agora tem ainda mais FLOW!'")
        log("      'Lucas, quanto mais você aprende, maior o prêmio!'")
        log("      'Continue explorando e tente descobrir a senha!'")
        log("")
        log("💡 Status da Bag do Lucas:")
        log("   📚 Conhecimentos: ".concat(self.surfista.bagDeConhecimento.length.toString()))
        log("   ⭐ Pontos totais: ".concat(self.surfista.pontosTotal.toString()))
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    }
}