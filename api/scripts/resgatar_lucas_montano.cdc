import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import SurfistaNFT from 0x25f823e2a115b2dc

/// Script para resgatar o surfista Lucas Montano
/// Cria NFT única com bag de conhecimento e presente inicial
transaction(presenteInicial: UFix64) {
    let minter: &SurfistaNFT.NFTMinter
    let collection: &{NonFungibleToken.CollectionPublic}
    let flowVault: &FlowToken.Vault

    prepare(signer: AuthAccount) {
        // Obter o minter
        self.minter = signer.borrow<&SurfistaNFT.NFTMinter>(
            from: SurfistaNFT.MinterStoragePath
        ) ?? panic("Não foi possível acessar o NFTMinter")

        // Criar coleção se não existir
        if signer.borrow<&SurfistaNFT.Collection>(from: SurfistaNFT.CollectionStoragePath) == nil {
            signer.save(<-SurfistaNFT.createEmptyCollection(), to: SurfistaNFT.CollectionStoragePath)
            signer.link<&SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic,NonFungibleToken.CollectionPublic,NonFungibleToken.Receiver,MetadataViews.ResolverCollection}>(
                SurfistaNFT.CollectionPublicPath,
                target: SurfistaNFT.CollectionStoragePath
            )
        }

        // Referência para a coleção
        self.collection = signer.getCapability(SurfistaNFT.CollectionPublicPath)
            .borrow<&{NonFungibleToken.CollectionPublic}>()
            ?? panic("Não foi possível obter a coleção")

        // Obter vault de FLOW para presente
        self.flowVault = signer.borrow<&FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Não foi possível acessar o FlowToken Vault")
    }

    execute {
        log("🌊🏄‍♂️ RESGATE ÉPICO NO WAVE ONFLOW!")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log("🌊 Uma onda gigantesca de 25 metros!")
        log("💥 Prancha quebrada!")
        log("🚨 Surfista em perigo!")
        log("")

        // Resgatar Lucas Montano com presente de boas-vindas
        let presenteVault <- self.flowVault.withdraw(amount: presenteInicial)
        let lucasID = self.minter.resgatarSurfista(
            nomeBase: "Lucas Montano",
            recipient: self.collection,
            presenteInicial: <-presenteVault
        )

        log("🎊 LUCAS MONTANO RESGATADO COM SUCESSO!")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log("")
        log("🏄‍♂️ SURFISTA: Lucas Montano")
        log("🆔 NFT ID: #".concat(lucasID.toString()))
        log("💰 Presente inicial: ".concat(presenteInicial.toString()).concat(" FLOW"))
        log("")
        log("📚 BAG DE CONHECIMENTO CRIADA!")
        log("   • 100 pontos iniciais por ser resgatado")
        log("   • 50 pontos bonus pelo presente de FLOW")
        log("   • Total: 150 pontos")
        log("")
        log("⚡ STATUS DO SUBMARINO:")
        log("   • Profundidade: 200m (Zona Abissal)")
        log("   • Energia: Crítica após o resgate")
        log("   • Sistemas: Danificados, precisam de reparo")
        log("")
        log("🎯 MISSÃO:")
        log("   Lucas precisa ajudar a consertar o submarino")
        log("   explorando os compartimentos e coletando conhecimento!")
        log("")
        log("💡 DICAS:")
        log("   • Digite 'ls' para ver os compartimentos")
        log("   • Cada arquivo explorado = +10 pontos")
        log("   • Cada comando = +5 pontos")
        log("   • Objetivo: Chegar na superfície (0m)")
        log("")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log("🎮 JOGO INICIADO! BOA SORTE, LUCAS MONTANO!")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    }
}