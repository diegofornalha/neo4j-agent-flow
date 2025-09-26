import NonFungibleToken from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import SurfistaNFT from 0x25f823e2a115b2dc

/// Transação para resgatar um surfista com presente inicial de FLOW
/// O presente fica armazenado dentro da NFT do surfista
///
transaction(nomeSurfista: String, presenteFlow: UFix64) {

    let minter: &SurfistaNFT.NFTMinter
    let recipient: &{NonFungibleToken.CollectionPublic}
    let flowVault: @FungibleToken.Vault

    prepare(signer: AuthAccount) {
        // Verificar se o usuário já tem uma coleção
        if signer.borrow<&SurfistaNFT.Collection>(from: SurfistaNFT.CollectionStoragePath) == nil {
            // Criar uma nova coleção
            signer.save(<-SurfistaNFT.createEmptyCollection(), to: SurfistaNFT.CollectionStoragePath)

            // Publicar a coleção
            signer.link<&{NonFungibleToken.CollectionPublic, SurfistaNFT.SurfistaCollectionPublic}>(
                SurfistaNFT.CollectionPublicPath,
                target: SurfistaNFT.CollectionStoragePath
            )
        }

        // Pegar referência do minter (assumindo que está na conta do contrato)
        let contractAccount = getAccount(0x25f823e2a115b2dc)
        self.minter = contractAccount
            .getCapability<&SurfistaNFT.NFTMinter>(SurfistaNFT.MinterStoragePath)
            .borrow()
            ?? panic("Não foi possível pegar o minter")

        // Pegar referência da coleção do destinatário
        self.recipient = signer
            .getCapability(SurfistaNFT.CollectionPublicPath)
            .borrow<&{NonFungibleToken.CollectionPublic}>()
            ?? panic("Não foi possível pegar a coleção do destinatário")

        // Preparar o presente de FLOW (se especificado)
        if presenteFlow > 0.0 {
            let flowVaultRef = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
                ?? panic("Não foi possível acessar o vault de FLOW")

            self.flowVault <- flowVaultRef.withdraw(amount: presenteFlow)
        } else {
            // Criar vault vazio se não houver presente
            self.flowVault <- FlowToken.createEmptyVault()
        }
    }

    execute {
        // Resgatar o surfista com presente de boas-vindas!
        let nftID = self.minter.resgatarSurfista(
            nomeBase: nomeSurfista,
            recipient: self.recipient,
            presenteInicial: <-self.flowVault
        )

        log("🏄 Surfista resgatado com sucesso!")
        log("📍 NFT ID: ".concat(nftID.toString()))
        log("🏷️ Nome: ".concat(nomeSurfista))

        if presenteFlow > 0.0 {
            log("🎁 Presente de boas-vindas: ".concat(presenteFlow.toString()).concat(" FLOW"))
            log("💰 O FLOW está seguro dentro da NFT do surfista!")
        }
    }

    post {
        self.recipient.getIDs().length > 0:
            "A NFT não foi criada corretamente"
    }
}