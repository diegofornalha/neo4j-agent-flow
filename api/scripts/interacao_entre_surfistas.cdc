import SurfistaNFT from 0x25f823e2a115b2dc
import NonFungibleToken from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// Script para permitir interação entre quaisquer dois surfistas
/// Eles podem compartilhar conhecimento, enviar mensagens e fazer desafios juntos
/// Ações cooperativas requerem pagamento em FLOW mas dão 2x mais resultados
transaction(
    meuID: UInt64,
    amigoID: UInt64,
    acao: String,
    mensagem: String?
) {
    let minhaNFT: &SurfistaNFT.NFT
    let colecaoAmigo: &SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic}

    prepare(signer: AuthAccount) {
        // Obter minha NFT
        let collection = signer.borrow<&SurfistaNFT.Collection>(
            from: SurfistaNFT.CollectionStoragePath
        ) ?? panic("Não encontrei sua coleção de surfistas")

        self.minhaNFT = collection.borrowSurfista(id: meuID)
            ?? panic("Você não tem essa NFT de surfista")

        // Obter coleção do amigo (assumindo que está na mesma conta por enquanto)
        self.colecaoAmigo = signer.getCapability(SurfistaNFT.CollectionPublicPath)
            .borrow<&SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic}>()
            ?? panic("Não foi possível acessar a coleção do amigo")
    }

    execute {
        // Adicionar como amigo
        self.minhaNFT.adicionarAmigo(amigoID: amigoID)

        // Realizar ação baseada no tipo
        switch acao {
            case "compartilhar_conhecimento":
                // Compartilhar conhecimento com desconto cooperativo
                log("📚 COMPARTILHAMENTO DE CONHECIMENTO")
                log("🏄 Surfista #".concat(meuID.toString()).concat(": 'Olha o que descobri!'"))
                log("🏄 Surfista #".concat(amigoID.toString()).concat(": 'Show! Vamos usar isso!'"))

                // Interação social é gratuita mas dá pontos
                self.minhaNFT.pontosTotal = self.minhaNFT.pontosTotal + 15
                if let amigoNFT = self.colecaoAmigo.borrowSurfista(id: amigoID) {
                    amigoNFT.pontosTotal = amigoNFT.pontosTotal + 15
                }

                log("✅ +15 pontos para cada (cooperação gratuita)")
                log("⚡ Submarino sobe 10 metros!")

            case "desafio_dupla":
                // Desafios em dupla dão MUITO mais pontos
                log("🎯 DESAFIO EM DUPLA")
                log("🏄 Surfista #".concat(meuID.toString()).concat(": 'Vamos consertar o motor juntos!'"))
                log("🏄 Surfista #".concat(amigoID.toString()).concat(": 'Eu pego as ferramentas, você o manual!'"))

                self.minhaNFT.pontosTotal = self.minhaNFT.pontosTotal + 30
                if let amigoNFT = self.colecaoAmigo.borrowSurfista(id: amigoID) {
                    amigoNFT.pontosTotal = amigoNFT.pontosTotal + 30
                }

                log("✅ +30 pontos para cada!")
                log("⚡ Submarino sobe 20 metros!")
                log("🔧 Motor 50% reparado!")

                emit SurfistaNFT.DesafioMultiplayer(
                    surfista1: meuID,
                    surfista2: amigoID,
                    tipo: "Reparo cooperativo"
                )

            case "ajuda_mutua":
                // Ajuda mútua beneficia ambos
                log("💪 AJUDA MÚTUA")
                log("🏄 Surfista #".concat(meuID.toString()).concat(": 'Deixa que eu te ajudo!'"))
                log("🏄 Surfista #".concat(amigoID.toString()).concat(": 'Valeu! Juntos somos mais fortes!'"))

                self.minhaNFT.pontosTotal = self.minhaNFT.pontosTotal + 25
                if let amigoNFT = self.colecaoAmigo.borrowSurfista(id: amigoID) {
                    amigoNFT.pontosTotal = amigoNFT.pontosTotal + 20

                    // Ambos sobem quando se ajudam
                    let energiaAtual = self.minhaNFT.energiaGasta
                    self.minhaNFT.atualizarProfundidade(energiaGasta: energiaAtual + 5.0)
                    amigoNFT.atualizarProfundidade(energiaGasta: amigoNFT.energiaGasta + 5.0)
                }

                log("✅ Surfista #".concat(meuID.toString()).concat(": +25 pontos | Surfista #").concat(amigoID.toString()).concat(": +20 pontos"))
                log("⚡ Ambos sobem 15 metros!")

            case "enviar_mensagem":
                if mensagem != nil {
                    if let amigoNFT = self.colecaoAmigo.borrowSurfista(id: amigoID) {
                        amigoNFT.receberMensagem(mensagem: mensagem!)
                        log("💬 Mensagem enviada!")
                    }
                }

            default:
                log("Ação não reconhecida")
        }

        // Emitir evento de interação
        emit SurfistaNFT.InteracaoEntreSurfistas(
            surfista1: meuID,
            surfista2: amigoID,
            acao: acao
        )
    }
}