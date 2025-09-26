import SurfistaNFT from 0x36395f9dde50ea27
import NonFungibleToken from 0x631e88ae7f1d7c20
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

/// Transaction para mintar NFT de surfista com pagamento real em FLOW
/// O FLOW será debitado da conta e depositado no vault da NFT
transaction(nomeSurfista: String, valorPresente: UFix64) {

    let minter: &SurfistaNFT.NFTMinter
    let collection: &{NonFungibleToken.CollectionPublic}
    let flowVault: &FlowToken.Vault

    prepare(signer: AuthAccount) {
        // Configurar coleção se não existir
        if signer.borrow<&SurfistaNFT.Collection>(from: /storage/SurfistaNFTCollection) == nil {
            let collection <- SurfistaNFT.createEmptyCollection()
            signer.save(<-collection, to: /storage/SurfistaNFTCollection)
            signer.link<&{NonFungibleToken.CollectionPublic, SurfistaNFT.SurfistaCollectionPublic}>(
                /public/SurfistaNFTCollection,
                target: /storage/SurfistaNFTCollection
            )
        }

        // Obter referências
        self.minter = signer.borrow<&SurfistaNFT.NFTMinter>(from: /storage/SurfistaNFTMinter)
            ?? panic("NFTMinter não encontrado")

        self.collection = signer.getCapability(/public/SurfistaNFTCollection)
            .borrow<&{NonFungibleToken.CollectionPublic}>()
            ?? panic("Coleção não encontrada")

        // Obter vault de FLOW para pagamento
        self.flowVault = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Vault de FLOW não encontrado")
    }

    execute {
        log("🌊 ═══════════════════════════════════════════")
        log("🏄 INICIANDO MINT DE NFT COM PAGAMENTO REAL")
        log("🌊 ═══════════════════════════════════════════")
        log("")
        log("👤 Surfista: ".concat(nomeSurfista))
        log("💰 Valor a debitar: ".concat(valorPresente.toString()).concat(" FLOW"))
        log("")

        // Verificar saldo antes
        let saldoAntes = self.flowVault.balance
        log("📊 Saldo ANTES: ".concat(saldoAntes.toString()).concat(" FLOW"))

        // Retirar FLOW da conta (débito real)
        let pagamento <- self.flowVault.withdraw(amount: valorPresente)
        log("✅ FLOW debitado da sua conta!")

        // Criar NFT com o FLOW como presente
        let nftID = self.minter.resgatarSurfista(
            nomeBase: nomeSurfista,
            recipient: self.collection,
            presenteInicial: <-pagamento
        )

        // Verificar saldo depois
        let saldoDepois = self.flowVault.balance
        log("📊 Saldo DEPOIS: ".concat(saldoDepois.toString()).concat(" FLOW"))
        log("💸 Total debitado: ".concat((saldoAntes - saldoDepois).toString()).concat(" FLOW"))
        log("")

        log("🎊 ═══════════════════════════════════════════")
        log("✅ NFT CRIADA COM SUCESSO!")
        log("🆔 NFT ID: #".concat(nftID.toString()))
        log("👤 Nome: ".concat(nomeSurfista))
        log("💰 FLOW no vault da NFT: ".concat(valorPresente.toString()))
        log("🎊 ═══════════════════════════════════════════")
        log("")
        log("⚡ O FLOW foi DEBITADO da sua conta e está")
        log("   armazenado DENTRO da NFT como tesouro!")
    }
}