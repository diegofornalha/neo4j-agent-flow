import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// WaveNFT - Sistema de nomes como NFTs para o Wave OnFlow Bootcamp
/// Cada nome registrado é um NFT único e transferível
access(all) contract WaveNFT: NonFungibleToken {

    /// Eventos padrão NFT
    access(all) event ContractInitialized()
    access(all) event Withdraw(id: UInt64, from: Address?)
    access(all) event Deposit(id: UInt64, to: Address?)
    access(all) event NameMinted(id: UInt64, name: String, owner: Address)
    access(all) event NameTransferred(id: UInt64, name: String, from: Address, to: Address)

    /// Paths de storage
    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath
    access(all) let MinterStoragePath: StoragePath

    /// Contador de NFTs
    access(all) var totalSupply: UInt64

    /// Mapeamento de nomes para IDs (para evitar duplicatas)
    access(contract) var nameToID: {String: UInt64}

    /// Preço base para registro
    access(all) var basePrice: UFix64

    /// NFT que representa um nome
    access(all) resource NFT: NonFungibleToken.NFT {
        access(all) let id: UInt64
        access(all) let name: String
        access(all) let mintedAt: UFix64
        access(all) let originalOwner: Address

        init(name: String, owner: Address) {
            self.id = WaveNFT.totalSupply
            self.name = name
            self.mintedAt = getCurrentBlock().timestamp
            self.originalOwner = owner

            WaveNFT.totalSupply = WaveNFT.totalSupply + 1
            WaveNFT.nameToID[name] = self.id
        }

        /// Cria uma coleção vazia para este NFT
        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <- WaveNFT.createEmptyCollection()
        }

        /// Retorna as views de metadados suportadas
        access(all) fun getViews(): [Type] {
            return [
                Type<MetadataViews.Display>(),
                Type<MetadataViews.Identity>(),
                Type<MetadataViews.Royalties>(),
                Type<MetadataViews.NFTCollectionData>(),
                Type<MetadataViews.NFTCollectionDisplay>()
            ]
        }

        /// Resolve uma view de metadados
        access(all) fun resolveView(_ view: Type): AnyStruct? {
            switch view {
                case Type<MetadataViews.Display>():
                    return MetadataViews.Display(
                        name: self.name,
                        description: "Wave Name NFT: ".concat(self.name).concat(" - Um nome único no Wave OnFlow Bootcamp"),
                        thumbnail: MetadataViews.HTTPFile(url: "https://wave.onflow.org/names/".concat(self.name).concat(".png"))
                    )
                case Type<MetadataViews.Identity>():
                    return MetadataViews.Identity(
                        uuid: self.uuid
                    )
                case Type<MetadataViews.Royalties>():
                    return MetadataViews.Royalties([])
                case Type<MetadataViews.NFTCollectionData>():
                    return MetadataViews.NFTCollectionData(
                        storagePath: WaveNFT.CollectionStoragePath,
                        publicPath: WaveNFT.CollectionPublicPath,
                        publicCollection: Type<&WaveNFT.Collection>(),
                        publicLinkedType: Type<&WaveNFT.Collection>(),
                        createEmptyCollectionFunction: (fun (): @{NonFungibleToken.Collection} {
                            return <-WaveNFT.createEmptyCollection()
                        })
                    )
                case Type<MetadataViews.NFTCollectionDisplay>():
                    return MetadataViews.NFTCollectionDisplay(
                        name: "Wave Name Collection",
                        description: "Coleção de nomes únicos do Wave OnFlow Bootcamp",
                        externalURL: MetadataViews.ExternalURL("https://wave.onflow.org"),
                        squareImage: MetadataViews.Media(
                            file: MetadataViews.HTTPFile(url: "https://wave.onflow.org/logo.png"),
                            mediaType: "image/png"
                        ),
                        bannerImage: MetadataViews.Media(
                            file: MetadataViews.HTTPFile(url: "https://wave.onflow.org/banner.png"),
                            mediaType: "image/png"
                        ),
                        socials: {}
                    )
            }
            return nil
        }

    }

    /// Coleção de NFTs
    access(all) resource Collection: NonFungibleToken.Provider, NonFungibleToken.Receiver, NonFungibleToken.CollectionPublic, MetadataViews.ResolverCollection {
        access(all) var ownedNFTs: @{UInt64: {NonFungibleToken.NFT}}

        init() {
            self.ownedNFTs <- {}
        }

        /// Retorna os tipos de NFT suportados
        access(all) fun getSupportedNFTTypes(): {Type: Bool} {
            return {Type<@WaveNFT.NFT>(): true}
        }

        /// Verifica se um tipo de NFT é suportado
        access(all) fun isSupportedNFTType(type: Type): Bool {
            return type == Type<@WaveNFT.NFT>()
        }

        /// Retorna o tamanho da coleção
        access(all) fun getLength(): Int {
            return self.ownedNFTs.length
        }

        /// Itera sobre cada ID na coleção
        access(all) fun forEachID(_ f: fun(UInt64): Bool): Void {
            for id in self.ownedNFTs.keys {
                if !f(id) {
                    break
                }
            }
        }

        /// Cria uma coleção vazia
        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <- create Collection()
        }

        /// Retira um NFT da coleção
        access(all) fun withdraw(withdrawID: UInt64): @{NonFungibleToken.NFT} {
            let token <- self.ownedNFTs.remove(key: withdrawID)
                ?? panic("NFT não existe na coleção")

            emit Withdraw(id: token.id, from: self.owner?.address)
            return <-token
        }

        /// Deposita um NFT na coleção
        access(all) fun deposit(token: @{NonFungibleToken.NFT}) {
            let token <- token as! @WaveNFT.NFT
            let id: UInt64 = token.id

            let oldToken <- self.ownedNFTs[id] <- token

            emit Deposit(id: id, to: self.owner?.address)

            destroy oldToken
        }

        /// Retorna lista de IDs na coleção
        access(all) fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        /// Pega referência de um NFT
        access(all) fun borrowNFT(id: UInt64): &{NonFungibleToken.NFT} {
            return (&self.ownedNFTs[id] as &{NonFungibleToken.NFT}?)!
        }

        /// Pega referência de um WaveNFT específico
        access(all) fun borrowWaveNFT(id: UInt64): &WaveNFT.NFT? {
            if self.ownedNFTs[id] != nil {
                let ref = (&self.ownedNFTs[id] as auth(NonFungibleToken.Withdraw) &{NonFungibleToken.NFT}?)!
                return ref as! &WaveNFT.NFT
            }
            return nil
        }

        /// Resolve view de um NFT
        access(all) fun borrowViewResolver(id: UInt64): &{MetadataViews.Resolver} {
            let nft = (&self.ownedNFTs[id] as auth(NonFungibleToken.Withdraw) &{NonFungibleToken.NFT}?)!
            let waveNFT = nft as! &WaveNFT.NFT
            return waveNFT
        }

    }

    /// Interface pública da coleção
    access(all) resource interface CollectionPublic {
        access(all) fun deposit(token: @{NonFungibleToken.NFT})
        access(all) fun getIDs(): [UInt64]
        access(all) fun borrowNFT(id: UInt64): &{NonFungibleToken.NFT}
        access(all) fun borrowWaveNFT(id: UInt64): &WaveNFT.NFT?
    }

    /// Recurso Minter para criar novos NFTs
    access(all) resource NFTMinter {

        /// Minta um novo nome NFT
        access(all) fun mintNFT(name: String, recipient: &{NonFungibleToken.CollectionPublic}, payment: @FlowToken.Vault) {
            pre {
                WaveNFT.nameToID[name] == nil: "Nome já existe!"
                payment.balance >= WaveNFT.calculatePrice(name): "Pagamento insuficiente"
            }

            // Destruir pagamento (ou transferir para treasury)
            destroy payment

            let owner = recipient.owner?.address ?? panic("Recipient sem owner")

            // Criar novo NFT
            let nft <- create NFT(name: name, owner: owner)
            let id = nft.id

            // Depositar na coleção do recipient
            recipient.deposit(token: <-nft)

            emit NameMinted(id: id, name: name, owner: owner)
        }
    }

    /// Calcula o preço baseado no tamanho do nome
    access(all) view fun calculatePrice(_ name: String): UFix64 {
        let length = name.length

        if length <= 3 {
            return self.basePrice * 100.0  // 100 FLOW
        } else if length <= 5 {
            return self.basePrice * 10.0   // 10 FLOW
        } else if length <= 8 {
            return self.basePrice * 5.0    // 5 FLOW
        }

        return self.basePrice  // 1 FLOW para nomes longos
    }

    /// Verifica se um nome já existe
    access(all) fun nameExists(_ name: String): Bool {
        return self.nameToID[name] != nil
    }

    /// Retorna o ID de um nome
    access(all) fun getNameID(_ name: String): UInt64? {
        return self.nameToID[name]
    }

    /// Cria uma coleção vazia
    access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
        return <- create Collection()
    }

    init() {
        // Inicializar paths
        self.CollectionStoragePath = /storage/waveNFTCollection
        self.CollectionPublicPath = /public/waveNFTCollection
        self.MinterStoragePath = /storage/waveNFTMinter

        // Inicializar variáveis
        self.totalSupply = 0
        self.nameToID = {}
        self.basePrice = 1.0  // 1 FLOW base

        // Criar Minter e salvar na conta do contrato
        let minter <- create NFTMinter()
        self.account.save(<-minter, to: self.MinterStoragePath)

        emit ContractInitialized()
    }
}