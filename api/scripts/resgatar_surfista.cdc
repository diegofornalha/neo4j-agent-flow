import NonFungibleToken from 0x631e88ae7f1d7c20
import SurfistaNFT from 0x25f823e2a115b2dc

/// Transação para resgatar um surfista criando sua NFT única
///
transaction(nomeSurfista: String) {

    let minter: &SurfistaNFT.NFTMinter
    let recipient: &{NonFungibleToken.CollectionPublic}

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
    }

    execute {
        // Resgatar o surfista sem presente inicial (vault vazio)
        let vaultVazio: @FungibleToken.Vault? <- nil
        let nftID = self.minter.resgatarSurfista(
            nomeBase: nomeSurfista,
            recipient: self.recipient,
            presenteInicial: <-vaultVazio
        )

        log("🏄 Surfista resgatado com sucesso!")
        log("📍 NFT ID: ".concat(nftID.toString()))
        log("🏷️ Nome: ".concat(nomeSurfista))
    }

    post {
        self.recipient.getIDs().length > 0:
            "A NFT não foi criada corretamente"
    }
}