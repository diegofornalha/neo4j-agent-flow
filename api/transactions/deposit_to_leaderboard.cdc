import SurfistaLeaderboard from 0x25f823e2a115b2dc
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Transação para depositar FLOW e atualizar score automaticamente
transaction(amount: UFix64) {

    let paymentVault: @{FungibleToken.Vault}
    let signer: Address

    prepare(signer: auth(Storage) &Account) {
        self.signer = signer.address

        // Pegar vault de FLOW
        let vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Vault de FLOW não encontrado")

        // Retirar quantidade especificada
        self.paymentVault <- vaultRef.withdraw(amount: amount)
    }

    execute {
        // Depositar no leaderboard (atualiza score automaticamente)
        SurfistaLeaderboard.depositTokens(
            from: self.signer,
            vault: <-self.paymentVault
        )

        log("✅ Depósito realizado com sucesso!")
        log("💰 Quantidade: ".concat(amount.toString()).concat(" FLOW"))
        log("🏄 Surfista: ".concat(self.signer.toString()))
    }
}