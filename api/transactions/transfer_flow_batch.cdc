import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Transferir FLOW para múltiplos destinatários
transaction(recipients: [Address], amounts: [UFix64]) {

    let vaultRef: auth(FungibleToken.Withdraw) &FlowToken.Vault

    prepare(signer: auth(Storage) &Account) {
        assert(recipients.length == amounts.length, message: "Arrays devem ter o mesmo tamanho")

        self.vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Vault de FLOW não encontrado")
    }

    execute {
        var i = 0
        while i < recipients.length {
            let recipient = getAccount(recipients[i])
            let receiverRef = recipient.capabilities
                .get<&{FungibleToken.Receiver}>(/public/flowTokenReceiver)
                .borrow()
                ?? panic("Receiver não encontrado para: ".concat(recipients[i].toString()))

            let payment <- self.vaultRef.withdraw(amount: amounts[i])
            receiverRef.deposit(from: <-payment)

            log("✅ Transferido ".concat(amounts[i].toString()).concat(" FLOW para ").concat(recipients[i].toString()))
            i = i + 1
        }

        log("🎉 Todas as transferências concluídas!")
    }
}