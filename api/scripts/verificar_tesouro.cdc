import TesouroProtegido from 0x25f823e2a115b2dc

/// Script para verificar o status do Tesouro Protegido
///
access(all) fun main(conta: Address): {String: AnyStruct} {

    let tesouro = getAccount(conta)
        .getCapability(TesouroProtegido.TesouroPublicPath)
        .borrow<&{TesouroProtegido.TesouroPublico}>()
        ?? panic("Não foi possível acessar o Tesouro Protegido")

    let saldo = tesouro.verSaldo()
    let historico = tesouro.verHistorico()

    log("🏴‍☠️ TESOURO PROTEGIDO DO SUBMARINO")
    log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log("💰 Saldo Total: ".concat(saldo.toString()).concat(" FLOW"))
    log("")

    if historico.length > 0 {
        log("📜 HISTÓRICO DE DEPÓSITOS:")
        var total = 0.0
        for deposito in historico {
            log("   • ".concat(deposito.amount.toString())
                .concat(" FLOW - ")
                .concat(deposito.motivo))
            total = total + deposito.amount
        }
        log("")
        log("💎 Total depositado: ".concat(total.toString()).concat(" FLOW"))
    } else {
        log("📜 Nenhum depósito ainda...")
    }

    log("")
    log("🔐 STATUS: PROTEGIDO POR SENHA")
    log("💡 Dica: Para obter dica da senha, tente várias vezes!")
    log("⚠️  Tentativas falhas: ".concat(TesouroProtegido.tentativasFalhas.toString()))
    log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return {
        "saldo": saldo,
        "numeroDepositos": historico.length,
        "tentativasFalhas": TesouroProtegido.tentativasFalhas,
        "status": "PROTEGIDO"
    }
}