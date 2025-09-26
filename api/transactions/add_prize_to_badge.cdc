import HackathonBadge from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Adiciona prêmio a um badge existente
transaction(badgeID: UInt64, prizeAmount: UFix64) {
    let badge: &HackathonBadge.NFT
    let prizeVault: @FlowToken.Vault

    prepare(signer: auth(Storage) &Account) {
        // Pega a coleção
        let collection = signer.storage
            .borrow<&HackathonBadge.Collection>(from: HackathonBadge.CollectionStoragePath)
            ?? panic("Coleção não encontrada!")

        // Pega referência do badge
        self.badge = collection.borrowHackathonBadgeNFT(id: badgeID)
            ?? panic("Badge não encontrado!")

        // Pega o vault de Flow
        let vaultRef = signer.storage
            .borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Vault não encontrado")

        // Retira o prêmio
        self.prizeVault <- vaultRef.withdraw(amount: prizeAmount) as! @FlowToken.Vault
    }

    execute {
        // Deposita prêmio no badge
        self.badge.depositPrize(from: <-self.prizeVault)

        log("Prêmio de ".concat(prizeAmount.toString()).concat(" FLOW adicionado ao Badge #").concat(badgeID.toString()))
        log("Saldo atual do prêmio: ".concat(self.badge.getPrizeBalance().toString()).concat(" FLOW"))
    }
}