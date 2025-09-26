import WaveEventPrizeNFT from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Adiciona prêmio a um NFT existente
transaction(nftID: UInt64, prizeAmount: UFix64) {
    let collection: &WaveEventPrizeNFT.Collection
    let prizeVault: @FlowToken.Vault

    prepare(signer: auth(Storage) &Account) {
        // Pega a coleção
        self.collection = signer.storage
            .borrow<&WaveEventPrizeNFT.Collection>(from: WaveEventPrizeNFT.CollectionStoragePath)
            ?? panic("Coleção não encontrada!")

        // Pega o vault de Flow
        let vaultRef = signer.storage
            .borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Vault não encontrado")

        // Retira o prêmio
        self.prizeVault <- vaultRef.withdraw(amount: prizeAmount) as! @FlowToken.Vault
    }

    execute {
        // Deposita prêmio no NFT
        self.collection.depositPrizeToNFT(id: nftID, prize: <-self.prizeVault)

        log("Prêmio de ".concat(prizeAmount.toString()).concat(" FLOW adicionado ao NFT #").concat(nftID.toString()))
    }
}