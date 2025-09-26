import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Transaction simples para transferir FLOW
/// Demonstra débito real de FLOW da conta
transaction(amount: UFix64, recipient: Address) {

    let sentVault: @{FungibleToken.Vault}

    prepare(signer: auth(BorrowValue) &Account) {
        // Obter referência do vault de FLOW
        let vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Could not borrow reference to the owner's Vault!")

        // Retirar FLOW (débito real)
        self.sentVault <- vaultRef.withdraw(amount: amount)

        log("✅ ".concat(amount.toString()).concat(" FLOW debitado da conta!"))
        log("📊 Saldo restante: ".concat(vaultRef.balance.toString()))
    }

    execute {
        // Obter o receiver do destinatário
        let receiverRef = getAccount(recipient)
            .capabilities.borrow<&{FungibleToken.Receiver}>(/public/flowTokenReceiver)
            ?? panic("Could not borrow receiver reference")

        // Depositar FLOW
        receiverRef.deposit(from: <-self.sentVault)

        log("✅ FLOW transferido com sucesso para ".concat(recipient.toString()))
    }
}