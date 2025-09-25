import WaveNFT from 0x36395f9dde50ea27
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Minta um novo NFT de nome
transaction(name: String, amount: UFix64) {
    let collection: &WaveNFT.Collection
    let vault: @FlowToken.Vault

    prepare(signer: auth(Storage) &Account) {
        // Pega a coleção do usuário
        self.collection = signer.storage
            .borrow<&WaveNFT.Collection>(from: WaveNFT.CollectionStoragePath)
            ?? panic("Coleção WaveNFT não encontrada. Execute setup primeiro!")

        // Pega o vault de Flow tokens
        let vaultRef = signer.storage
            .borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Vault de Flow não encontrado")

        // Retira o pagamento
        self.vault <- vaultRef.withdraw(amount: amount) as! @FlowToken.Vault
    }

    execute {
        // Minta o NFT
        WaveNFT.mintNFT(
            name: name,
            recipient: self.collection,
            payment: <-self.vault
        )

        log("NFT '".concat(name).concat("' mintado com sucesso!"))
    }
}