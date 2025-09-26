import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import TesouroProtegido from 0x25f823e2a115b2dc

/// SurfistaNFT - NFT única para cada surfista resgatado
/// Armazena o nome, progresso e "bag de conhecimento" do surfista
///
access(all) contract SurfistaNFT: NonFungibleToken {

    /// Total de NFTs mintadas
    access(all) var totalSupply: UInt64

    /// Registro de nomes para evitar duplicatas
    /// Mapeia nome base -> quantidade de surfistas com esse nome
    access(all) var nomeRegistry: {String: UInt64}

    /// Eventos padrão NonFungibleToken
    access(all) event ContractInitialized()
    access(all) event Withdraw(id: UInt64, from: Address?)
    access(all) event Deposit(id: UInt64, to: Address?)

    /// Eventos customizados
    access(all) event SurfistaResgatado(id: UInt64, nome: String, address: Address)
    access(all) event ConhecimentoAdicionado(id: UInt64, conhecimento: String)
    access(all) event TesouroEncontrado(id: UInt64, tesouro: String, pontos: UInt64)
    access(all) event InteracaoEntreSurfistas(surfista1: UInt64, surfista2: UInt64, acao: String)
    access(all) event DesafioMultiplayer(surfista1: UInt64, surfista2: UInt64, tipo: String)

    /// Caminhos de storage
    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath
    access(all) let MinterStoragePath: StoragePath

    /// Estrutura de Conhecimento
    access(all) struct Conhecimento {
        access(all) let tipo: String  // "comando", "arquivo", "funcionalidade", "tesouro"
        access(all) let descricao: String
        access(all) let pontos: UInt64
        access(all) let timestamp: UFix64

        init(tipo: String, descricao: String, pontos: UInt64) {
            self.tipo = tipo
            self.descricao = descricao
            self.pontos = pontos
            self.timestamp = getCurrentBlock().timestamp
        }
    }

    /// NFT do Surfista
    access(all) resource NFT: NonFungibleToken.INFT, MetadataViews.Resolver {
        access(all) let id: UInt64
        access(all) let nome: String                    // Nome do surfista (ex: "Diego")
        access(all) let dataResgate: UFix64             // Quando foi resgatado
        access(all) var profundidadeAtual: UInt64       // Profundidade atual do submarino
        access(all) var energiaGasta: UFix64            // Total de FLOW gasto
        access(all) var bagDeConhecimento: [Conhecimento] // Conhecimentos adquiridos
        access(all) var pontosTotal: UInt64             // Pontos totais acumulados
        access(all) var conquistas: {String: Bool}      // Conquistas desbloqueadas
        access(all) var amigos: [UInt64]                // IDs dos outros surfistas conhecidos
        access(all) var mensagensRecebidas: [String]    // Mensagens de outros surfistas

        /// Vault embarcado para receber recompensas em FLOW
        access(self) let flowVault: @FlowToken.Vault

        init(
            id: UInt64,
            nome: String
        ) {
            self.id = id
            self.nome = nome
            self.dataResgate = getCurrentBlock().timestamp
            self.profundidadeAtual = 200  // Começa no fundo do oceano
            self.energiaGasta = 0.0
            self.bagDeConhecimento = []
            self.pontosTotal = 0
            self.conquistas = {}
            self.amigos = []
            self.mensagensRecebidas = []

            // Criar vault vazio para recompensas
            self.flowVault <- FlowToken.createEmptyVault() as! @FlowToken.Vault
        }

        /// Adiciona conhecimento à bag mediante pagamento de taxa
        /// Taxa: 0.1 FLOW por conhecimento básico, mais caro para conhecimentos raros
        access(all) fun adicionarConhecimento(
            tipo: String,
            descricao: String,
            pontos: UInt64,
            pagamento: @FungibleToken.Vault
        ) {
            // Calcular taxa baseada no tipo de conhecimento
            var taxaRequerida = 0.1  // Taxa base

            switch tipo {
                case "comando":
                    taxaRequerida = 0.1  // Comandos são baratos
                case "arquivo":
                    taxaRequerida = 0.2  // Arquivos custam mais
                case "funcionalidade":
                    taxaRequerida = 0.5  // Funcionalidades são caras
                case "tesouro":
                    taxaRequerida = 1.0  // Tesouros são muito caros
                case "conquista":
                    taxaRequerida = 2.0  // Conquistas são as mais caras
                default:
                    taxaRequerida = 0.1
            }

            // Verificar se o pagamento é suficiente
            assert(
                pagamento.balance >= taxaRequerida,
                message: "Pagamento insuficiente! Necessário: ".concat(taxaRequerida.toString()).concat(" FLOW")
            )

            // Enviar pagamento para o Tesouro Protegido!
            let tesouro = getAccount(0x25f823e2a115b2dc)
                .getCapability(TesouroProtegido.TesouroPublicPath)
                .borrow<&{TesouroProtegido.TesouroPublico}>()
                ?? panic("Não foi possível acessar o Tesouro Protegido")

            let motivo = "Conhecimento: ".concat(tipo).concat(" - ").concat(descricao)
            tesouro.depositar(from: <-pagamento, motivo: motivo)

            // Adicionar o conhecimento após pagamento
            let conhecimento = Conhecimento(tipo: tipo, descricao: descricao, pontos: pontos)
            self.bagDeConhecimento.append(conhecimento)
            self.pontosTotal = self.pontosTotal + pontos

            // Verificar conquistas
            self.verificarConquistas()

            emit ConhecimentoAdicionado(id: self.id, conhecimento: descricao)
            emit TesouroEncontrado(id: self.id, tesouro: "Pagou ".concat(taxaRequerida.toString()).concat(" FLOW"), pontos: pontos)
        }

        /// Atualiza profundidade baseada na energia gasta
        access(all) fun atualizarProfundidade(energiaGasta: UFix64) {
            self.energiaGasta = energiaGasta
            // Cada 1000 FLOW = 100% energia = sobe 200m
            let percentual = (energiaGasta / 1000.0) * 100.0
            let profundidade = 200.0 - (percentual * 2.0)
            self.profundidadeAtual = UInt64(profundidade > 0.0 ? profundidade : 0.0)
        }

        /// Verifica e atualiza conquistas
        access(self) fun verificarConquistas() {
            // Wave Rider - Completou o tutorial
            if self.bagDeConhecimento.length >= 1 {
                self.conquistas["Wave Rider"] = true
            }

            // Deep Diver - Explorou 5 pastas
            let pastas = self.bagDeConhecimento.filter(fun(c: Conhecimento): Bool {
                return c.tipo == "arquivo"
            })
            if pastas.length >= 5 {
                self.conquistas["Deep Diver"] = true
            }

            // Flow Master - NFT criada (sempre true)
            self.conquistas["Flow Master"] = true

            // Treasure Hunter - 100 pontos
            if self.pontosTotal >= 100 {
                self.conquistas["Treasure Hunter"] = true
            }

            // Rescue Complete - Chegou à superfície
            if self.profundidadeAtual <= 10 {
                self.conquistas["Rescue Complete"] = true
            }
        }

        /// Deposita recompensas FLOW no vault interno
        access(all) fun depositarRecompensa(from: @FungibleToken.Vault) {
            self.flowVault.deposit(from: <-from)
        }

        /// Retira recompensas FLOW (apenas o dono pode fazer)
        access(all) fun retirarRecompensa(amount: UFix64): @FungibleToken.Vault {
            return <-self.flowVault.withdraw(amount: amount)
        }

        /// Verifica saldo de recompensas
        access(all) fun saldoRecompensas(): UFix64 {
            return self.flowVault.balance
        }

        /// Adiciona um amigo surfista (interação social é gratuita)
        access(all) fun adicionarAmigo(amigoID: UInt64) {
            if !self.amigos.contains(amigoID) {
                self.amigos.append(amigoID)
                // Interações sociais dão pontos bonus sem custo
                self.pontosTotal = self.pontosTotal + 20

                // Adicionar conquista social
                if self.amigos.length >= 5 {
                    self.conquistas["Social Surfer"] = true
                }

                emit InteracaoEntreSurfistas(surfista1: self.id, surfista2: amigoID, acao: "Amizade")
            }
        }

        /// Envia mensagem para este surfista
        access(all) fun receberMensagem(mensagem: String) {
            self.mensagensRecebidas.append(mensagem)
        }

        access(all) fun getViews(): [Type] {
            return [
                Type<MetadataViews.Display>(),
                Type<MetadataViews.NFTCollectionData>(),
                Type<MetadataViews.NFTCollectionDisplay>()
            ]
        }

        access(all) fun resolveView(_ view: Type): AnyStruct? {
            switch view {
                case Type<MetadataViews.Display>():
                    return MetadataViews.Display(
                        name: "Surfista ".concat(self.nome),
                        description: "NFT do surfista resgatado no Wave OnFlow Bootcamp. Profundidade: "
                            .concat(self.profundidadeAtual.toString())
                            .concat("m | Pontos: ")
                            .concat(self.pontosTotal.toString()),
                        thumbnail: MetadataViews.HTTPFile(
                            url: "https://emoji.surf/🏄"
                        )
                    )

                case Type<MetadataViews.NFTCollectionData>():
                    return MetadataViews.NFTCollectionData(
                        storagePath: SurfistaNFT.CollectionStoragePath,
                        publicPath: SurfistaNFT.CollectionPublicPath,
                        providerPath: /private/surfistaNFTCollection,
                        publicCollection: Type<&SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic}>(),
                        publicLinkedType: Type<&SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic,NonFungibleToken.CollectionPublic,NonFungibleToken.Receiver,MetadataViews.ResolverCollection}>(),
                        providerLinkedType: Type<&SurfistaNFT.Collection{SurfistaNFT.SurfistaCollectionPublic,NonFungibleToken.CollectionPublic,NonFungibleToken.Provider,MetadataViews.ResolverCollection}>(),
                        createEmptyCollectionFunction: (fun (): @NonFungibleToken.Collection {
                            return <-SurfistaNFT.createEmptyCollection()
                        })
                    )

                case Type<MetadataViews.NFTCollectionDisplay>():
                    return MetadataViews.NFTCollectionDisplay(
                        name: "Wave OnFlow Surfistas",
                        description: "NFTs dos surfistas resgatados no bootcamp Wave OnFlow",
                        externalURL: MetadataViews.ExternalURL("https://flow.com"),
                        squareImage: MetadataViews.Media(
                            file: MetadataViews.HTTPFile(url: "https://emoji.surf/🏄"),
                            mediaType: "image/png"
                        ),
                        bannerImage: MetadataViews.Media(
                            file: MetadataViews.HTTPFile(url: "https://emoji.surf/🌊"),
                            mediaType: "image/png"
                        ),
                        socials: {}
                    )
            }
            return nil
        }

        destroy() {
            destroy self.flowVault
        }
    }

    /// Interface pública da coleção
    access(all) resource interface SurfistaCollectionPublic {
        access(all) fun deposit(token: @NonFungibleToken.NFT)
        access(all) fun getIDs(): [UInt64]
        access(all) fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
        access(all) fun borrowSurfista(id: UInt64): &SurfistaNFT.NFT? {
            post {
                (result == nil) || (result?.id == id):
                    "Cannot borrow Surfista reference: the ID of the returned reference is incorrect"
            }
        }
    }

    /// Coleção de NFTs do Surfista
    access(all) resource Collection: SurfistaCollectionPublic, NonFungibleToken.Provider, NonFungibleToken.Receiver, NonFungibleToken.CollectionPublic, MetadataViews.ResolverCollection {
        access(all) var ownedNFTs: @{UInt64: NonFungibleToken.NFT}

        init () {
            self.ownedNFTs <- {}
        }

        access(all) fun withdraw(withdrawID: UInt64): @NonFungibleToken.NFT {
            let token <- self.ownedNFTs.remove(key: withdrawID) ?? panic("NFT não encontrada")

            emit Withdraw(id: token.id, from: self.owner?.address)

            return <-token
        }

        access(all) fun deposit(token: @NonFungibleToken.NFT) {
            let token <- token as! @SurfistaNFT.NFT

            let id: UInt64 = token.id
            let oldToken <- self.ownedNFTs[id] <- token

            emit Deposit(id: id, to: self.owner?.address)

            destroy oldToken
        }

        access(all) fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        access(all) fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
            return (&self.ownedNFTs[id] as &NonFungibleToken.NFT?)!
        }

        access(all) fun borrowSurfista(id: UInt64): &SurfistaNFT.NFT? {
            if self.ownedNFTs[id] != nil {
                let ref = (&self.ownedNFTs[id] as auth &NonFungibleToken.NFT?)!
                return ref as! &SurfistaNFT.NFT
            }
            return nil
        }

        access(all) fun borrowViewResolver(id: UInt64): &AnyResource{MetadataViews.Resolver} {
            let nft = (&self.ownedNFTs[id] as auth &NonFungibleToken.NFT?)!
            let surfista = nft as! &SurfistaNFT.NFT
            return surfista as &AnyResource{MetadataViews.Resolver}
        }

        destroy() {
            destroy self.ownedNFTs
        }
    }

    /// Cria uma coleção vazia
    access(all) fun createEmptyCollection(): @NonFungibleToken.Collection {
        return <- create Collection()
    }

    /// Resource de Minter - apenas o admin pode mintar
    access(all) resource NFTMinter {

        /// Resgata um surfista criando sua NFT única
        /// Se o nome já existir, adiciona #2, #3, etc.
        /// Opcionalmente deposita FLOW inicial como presente de boas-vindas
        access(all) fun resgatarSurfista(
            nomeBase: String,
            recipient: &{NonFungibleToken.CollectionPublic},
            presenteInicial: @FungibleToken.Vault?
        ): UInt64 {
            let id = SurfistaNFT.totalSupply
            SurfistaNFT.totalSupply = SurfistaNFT.totalSupply + 1

            // Verificar se o nome já existe e criar nome único
            var nomeFinal = nomeBase
            if SurfistaNFT.nomeRegistry[nomeBase] != nil {
                // Nome já existe, adicionar número
                let count = SurfistaNFT.nomeRegistry[nomeBase]! + 1
                SurfistaNFT.nomeRegistry[nomeBase] = count
                nomeFinal = nomeBase.concat("#").concat(count.toString())
            } else {
                // Primeiro surfista com esse nome
                SurfistaNFT.nomeRegistry[nomeBase] = 1
            }

            // Criar a NFT do surfista com nome único
            let surfista <- create NFT(
                id: id,
                nome: nomeFinal
            )

            // Se houver presente inicial, enviar para o Tesouro Protegido
            if presenteInicial != nil {
                let presente <- presenteInicial!
                let valor = presente.balance

                // Acessar o Tesouro Protegido
                let tesouro = getAccount(0x25f823e2a115b2dc)
                    .getCapability(TesouroProtegido.TesouroPublicPath)
                    .borrow<&{TesouroProtegido.TesouroPublico}>()
                    ?? panic("Não foi possível acessar o Tesouro Protegido")

                let motivo = "Presente de boas-vindas para ".concat(nomeFinal)
                tesouro.depositar(from: <-presente, motivo: motivo)

                // Dar pontos bonus pelo presente (sem adicionar à bag)
                surfista.pontosTotal = 100  // Pontos iniciais de resgate

                emit TesouroEncontrado(
                    id: id,
                    tesouro: "Presente inicial: ".concat(valor.toString()).concat(" FLOW"),
                    pontos: 100
                )
            } else {
                destroy presenteInicial
                // Mesmo sem presente, ganha pontos iniciais
                surfista.pontosTotal = 50
            }

            emit SurfistaResgatado(id: id, nome: nomeFinal, address: recipient.owner?.address ?? 0x0)

            recipient.deposit(token: <-surfista)

            return id
        }
    }

    init() {
        self.totalSupply = 0
        self.nomeRegistry = {}

        self.CollectionStoragePath = /storage/surfistaNFTCollection
        self.CollectionPublicPath = /public/surfistaNFTCollection
        self.MinterStoragePath = /storage/surfistaNFTMinter

        // Criar o Minter
        let minter <- create NFTMinter()
        self.account.save(<-minter, to: self.MinterStoragePath)

        emit ContractInitialized()
    }
}