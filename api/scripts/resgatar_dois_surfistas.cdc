import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import SurfistaNFT from 0x25f823e2a115b2dc

/// Script para criar NFTs para Diego Fornalha (dono do submarino) e outro surfista resgatado
/// Diego Fornalha é o dono do submarino que já está a bordo
/// O segundo surfista pode ter qualquer nome
transaction(nomeSurfistaResgatado: String, presenteSurfista: UFix64, presenteFornalha: UFix64) {
    let minter: &SurfistaNFT.NFTMinter
    let surfistaCollection: &{NonFungibleToken.CollectionPublic}
    let fornalhaCollection: &{NonFungibleToken.CollectionPublic}
    let flowVault: &FlowToken.Vault

    prepare(signer: AuthAccount) {
        // Obter o minter
        self.minter = signer.borrow<&SurfistaNFT.NFTMinter>(
            from: SurfistaNFT.MinterStoragePath
        ) ?? panic("Não foi possível acessar o NFTMinter")

        // Criar coleções se não existirem
        if signer.borrow<&SurfistaNFT.Collection>(from: SurfistaNFT.CollectionStoragePath) == nil {
            signer.save(<-SurfistaNFT.createEmptyCollection(), to: SurfistaNFT.CollectionStoragePath)
            signer.link<&SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic,NonFungibleToken.CollectionPublic,NonFungibleToken.Receiver,MetadataViews.ResolverCollection}>(
                SurfistaNFT.CollectionPublicPath,
                target: SurfistaNFT.CollectionStoragePath
            )
        }

        // Referencias para as coleções
        self.surfistaCollection = signer.getCapability(SurfistaNFT.CollectionPublicPath)
            .borrow<&{NonFungibleToken.CollectionPublic}>()
            ?? panic("Não foi possível obter a coleção para o surfista resgatado")

        self.fornalhaCollection = signer.getCapability(SurfistaNFT.CollectionPublicPath)
            .borrow<&{NonFungibleToken.CollectionPublic}>()
            ?? panic("Não foi possível obter a coleção para Fornalha")

        // Obter vault de FLOW para presentes
        self.flowVault = signer.borrow<&FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Não foi possível acessar o FlowToken Vault")
    }

    execute {
        log("🌊 RESGATE ÉPICO DE DOIS SURFISTAS!")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log("Uma onda de 30 metros quebrou duas pranchas!")
        log("")

        // Resgatar surfista com presente de boas-vindas
        let presenteSurfistaVault <- self.flowVault.withdraw(amount: presenteSurfista)
        let surfistaID = self.minter.resgatarSurfista(
            nomeBase: nomeSurfistaResgatado,
            recipient: self.surfistaCollection,
            presenteInicial: <-presenteSurfistaVault
        )

        log("🏄 ".concat(nomeSurfistaResgatado.toUpper()).concat(" (SURFISTA RESGATADO)"))
        log("   • Surfista radical tentando recorde mundial")
        log("   • NFT ID: #".concat(surfistaID.toString()))
        log("   • Presente inicial: ".concat(presenteSurfista.toString()).concat(" FLOW"))
        log("")

        // Criar NFT para Diego Fornalha (dono do submarino)
        let presenteFornalhaVault <- self.flowVault.withdraw(amount: presenteFornalha)
        let fornalhaID = self.minter.resgatarSurfista(
            nomeBase: "Diego Fornalha",
            recipient: self.fornalhaCollection,
            presenteInicial: <-presenteFornalhaVault
        )

        log("🏄‍♂️ DIEGO FORNALHA (DONO DO SUBMARINO)")
        log("   • Operador do submarino de resgate")
        log("   • NFT ID: #".concat(fornalhaID.toString()))
        log("   • Presente inicial: ".concat(presenteFornalha.toString()).concat(" FLOW"))
        log("")

        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log("⚠️  SITUAÇÃO CRÍTICA:")
        log("   • Diego e ".concat(nomeSurfistaResgatado).concat(" a bordo = Submarino 50m mais fundo!"))
        log("   • Profundidade inicial: 250m (Zona Abissal)")
        log("   • Oxigênio limitado para 2 pessoas")
        log("")
        log("✨ VANTAGENS DO MODO MULTIPLAYER:")
        log("   • Ações cooperativas = 2x mais pontos")
        log("   • Trabalho em equipe = Subida mais rápida")
        log("   • Competições amigáveis = Pontos bonus")
        log("")
        log("🎮 MODO COOPERATIVO ATIVADO!")
        log("🤝 Diego Fornalha e ".concat(nomeSurfistaResgatado).concat(" agora são parceiros de sobrevivência!"))
        log("🚢 Juntos vão consertar o submarino e chegar à superfície!")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    }
}