import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868
import ViewResolver from 0x631e88ae7f1d7c20

/// SurferNFT - NFT de surfista no Wave OnFlow Bootcamp
/// Cada participante é um surfista resgatado pelo submarino
access(all) contract SurferNFT: NonFungibleToken {

    /// Eventos
    access(all) event ContractInitialized()
    access(all) event Withdraw(id: UInt64, from: Address?)
    access(all) event Deposit(id: UInt64, to: Address?)
    access(all) event SurferRescued(id: UInt64, name: String, wallet: Address, depth: Int)
    access(all) event EnergyBoost(id: UInt64, amount: UFix64, newDepth: Int)
    access(all) event TreasureFound(id: UInt64, treasure: String, points: Int)

    /// Paths
    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath
    access(all) let MinterStoragePath: StoragePath

    /// Estado
    access(all) var totalSupply: UInt64
    access(all) var surfersRegistry: {String: UInt64}  // nome -> id

    /// Status de profundidade
    access(all) enum DepthLevel: UInt8 {
        access(all) case surface      // 0-10m: Salvos!
        access(all) case shallow      // 10-50m: Muito seguro
        access(all) case medium       // 50-100m: Seguro
        access(all) case deep         // 100-200m: Atenção!
        access(all) case abyss        // 200m+: Perigo!
    }

    /// NFT do Surfista
    access(all) resource NFT: NonFungibleToken.NFT {
        access(all) let id: UInt64
        access(all) let name: String           // Nome do surfista
        access(all) let rescuedAt: UFix64      // Quando foi resgatado
        access(all) let wallet: Address        // Carteira do surfista

        /// Estado do submarino
        access(all) var currentDepth: Int      // Profundidade atual em metros
        access(all) var energy: UFix64         // Energia do submarino
        access(all) var treasuresFound: [String]  // Tesouros descobertos
        access(all) var totalPoints: Int       // Pontos totais

        /// Vault para recompensas em FLOW
        access(all) var rewardVault: @FlowToken.Vault

        init(
            id: UInt64,
            name: String,
            wallet: Address,
            initialReward: @FlowToken.Vault?
        ) {
            self.id = id
            self.name = name
            self.wallet = wallet
            self.rescuedAt = getCurrentBlock().timestamp

            // Estado inicial: profundo após o resgate
            self.currentDepth = 75  // Começa em 75m (médio)
            self.energy = 50.0       // Energia inicial limitada
            self.treasuresFound = []
            self.totalPoints = 0

            // Inicializar vault de recompensas
            if let reward <- initialReward {
                self.rewardVault <- reward
            } else {
                self.rewardVault <- FlowToken.createEmptyVault(vaultType: Type<@FlowToken.Vault>()) as! @FlowToken.Vault
            }
        }

        /// Gastar FLOW para ganhar energia e subir
        access(all) fun boostEnergy(payment: @FlowToken.Vault): Int {
            let amount = payment.balance
            self.rewardVault.deposit(from: <-payment)

            // Conversão: 1 FLOW = 10 energia = 5m subida
            let energyGained = amount * 10.0
            self.energy = self.energy + energyGained

            let metersUp = Int(amount * 5.0)
            self.currentDepth = self.currentDepth - metersUp
            if self.currentDepth < 0 {
                self.currentDepth = 0  // Chegou na superfície!
            }

            emit EnergyBoost(id: self.id, amount: amount, newDepth: self.currentDepth)
            return self.currentDepth
        }

        /// Explorar e ganhar tesouros (ação gratuita)
        access(all) fun explore(location: String): Int {
            // Cada exploração dá pontos e sobe um pouco
            self.treasuresFound.append(location)
            self.totalPoints = self.totalPoints + 5

            // Sobe 3 metros por exploração
            self.currentDepth = self.currentDepth - 3
            if self.currentDepth < 0 {
                self.currentDepth = 0
            }

            emit TreasureFound(id: self.id, treasure: location, points: 5)
            return self.totalPoints
        }

        /// Obter nível de profundidade atual
        access(all) view fun getDepthLevel(): DepthLevel {
            if self.currentDepth <= 10 {
                return DepthLevel.surface
            } else if self.currentDepth <= 50 {
                return DepthLevel.shallow
            } else if self.currentDepth <= 100 {
                return DepthLevel.medium
            } else if self.currentDepth <= 200 {
                return DepthLevel.deep
            } else {
                return DepthLevel.abyss
            }
        }

        /// Status completo do surfista
        access(all) view fun getStatus(): String {
            let level = self.getDepthLevel()
            var status = "🏄 "

            switch level {
                case DepthLevel.surface:
                    status = status.concat("SALVO! Na superfície!")
                case DepthLevel.shallow:
                    status = status.concat("Muito seguro - águas rasas")
                case DepthLevel.medium:
                    status = status.concat("Seguro - profundidade média")
                case DepthLevel.deep:
                    status = status.concat("⚠️ Atenção! Muito profundo")
                case DepthLevel.abyss:
                    status = status.concat("💀 PERIGO! Abismo!")
            }

            return status.concat(" (").concat(self.currentDepth.toString()).concat("m)")
        }

        /// Sacar recompensas
        access(all) fun withdrawReward(amount: UFix64): @FlowToken.Vault {
            return <- self.rewardVault.withdraw(amount: amount) as! @FlowToken.Vault
        }

        /// Saldo de recompensas
        access(all) view fun getRewardBalance(): UFix64 {
            return self.rewardVault.balance
        }

        /// Criar coleção vazia
        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <- SurferNFT.createEmptyCollection(nftType: Type<@NFT>())
        }

        /// Views para MetadataViews
        access(all) view fun getViews(): [Type] {
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
                        name: "Surfista ".concat(self.name),
                        description: self.getStatus()
                            .concat(" | Energia: ").concat(self.energy.toString())
                            .concat(" | Pontos: ").concat(self.totalPoints.toString())
                            .concat(" | Tesouros: ").concat(self.treasuresFound.length.toString()),
                        thumbnail: MetadataViews.HTTPFile(
                            url: "https://raw.githubusercontent.com/onflow/fcl-js/master/packages/fcl/assets/flow.png"
                        )
                    )
                case Type<MetadataViews.NFTCollectionData>():
                    return SurferNFT.resolveContractView(resourceType: Type<@NFT>(), viewType: Type<MetadataViews.NFTCollectionData>())
                case Type<MetadataViews.NFTCollectionDisplay>():
                    return SurferNFT.resolveContractView(resourceType: Type<@NFT>(), viewType: Type<MetadataViews.NFTCollectionDisplay>())
            }
            return nil
        }
    }

    /// Interface pública da coleção
    access(all) resource interface SurferCollectionPublic {
        access(all) fun deposit(token: @{NonFungibleToken.NFT})
        access(all) view fun getIDs(): [UInt64]
        access(all) fun borrowSurferNFT(id: UInt64): &SurferNFT.NFT?
    }

    /// Coleção de Surfistas
    access(all) resource Collection: SurferCollectionPublic, NonFungibleToken.Collection {
        access(all) var ownedNFTs: @{UInt64: {NonFungibleToken.NFT}}

        init() {
            self.ownedNFTs <- {}
        }

        access(NonFungibleToken.Withdraw) fun withdraw(withdrawID: UInt64): @{NonFungibleToken.NFT} {
            let token <- self.ownedNFTs.remove(key: withdrawID)!
            emit Withdraw(id: token.id, from: self.owner?.address)
            return <-token
        }

        access(all) fun deposit(token: @{NonFungibleToken.NFT}) {
            let token <- token as! @SurferNFT.NFT
            let id: UInt64 = token.id
            let oldToken <- self.ownedNFTs[id] <- token
            destroy oldToken
            emit Deposit(id: id, to: self.owner?.address)
        }

        access(all) view fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        access(all) view fun borrowNFT(_ id: UInt64): &{NonFungibleToken.NFT}? {
            return &self.ownedNFTs[id]
        }

        access(all) fun borrowSurferNFT(id: UInt64): &SurferNFT.NFT? {
            if let ref = &self.ownedNFTs[id] as &{NonFungibleToken.NFT}? {
                return ref as! &SurferNFT.NFT
            }
            return nil
        }

        access(all) view fun borrowViewResolver(id: UInt64): &{ViewResolver.Resolver}? {
            if let nft = &self.ownedNFTs[id] as &{NonFungibleToken.NFT}? {
                return nft as &{ViewResolver.Resolver}
            }
            return nil
        }

        access(all) view fun getSupportedNFTTypes(): {Type: Bool} {
            return {Type<@NFT>(): true}
        }

        access(all) view fun isSupportedNFTType(type: Type): Bool {
            return type == Type<@NFT>()
        }

        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <- SurferNFT.createEmptyCollection(nftType: Type<@SurferNFT.NFT>())
        }
    }

    /// Criar coleção vazia
    access(all) fun createEmptyCollection(nftType: Type): @{NonFungibleToken.Collection} {
        return <- create Collection()
    }

    /// Resgatar um novo surfista (mintar NFT)
    access(all) fun rescueSurfer(
        name: String,
        wallet: Address,
        collection: &{SurferCollectionPublic},
        initialReward: @FlowToken.Vault?
    ): UInt64 {
        // Verificar se já foi resgatado
        assert(!self.surfersRegistry.containsKey(name), message: "Surfista já foi resgatado!")

        self.totalSupply = self.totalSupply + 1
        let newID = self.totalSupply

        // Criar o NFT do surfista
        let surfer <- create NFT(
            id: newID,
            name: name,
            wallet: wallet,
            initialReward: <-initialReward
        )

        // Registrar
        self.surfersRegistry[name] = newID

        // Depositar na coleção
        collection.deposit(token: <-surfer)

        emit SurferRescued(id: newID, name: name, wallet: wallet, depth: 75)

        return newID
    }

    /// Verificar se surfista já foi resgatado
    access(all) view fun isSurferRescued(name: String): Bool {
        return self.surfersRegistry.containsKey(name)
    }

    /// Obter ID do surfista
    access(all) view fun getSurferID(name: String): UInt64? {
        return self.surfersRegistry[name]
    }

    /// Contract views
    access(all) view fun getContractViews(resourceType: Type?): [Type] {
        return [
            Type<MetadataViews.NFTCollectionData>(),
            Type<MetadataViews.NFTCollectionDisplay>()
        ]
    }

    access(all) fun resolveContractView(resourceType: Type?, viewType: Type): AnyStruct? {
        switch viewType {
            case Type<MetadataViews.NFTCollectionData>():
                return MetadataViews.NFTCollectionData(
                    storagePath: self.CollectionStoragePath,
                    publicPath: self.CollectionPublicPath,
                    publicCollection: Type<&SurferNFT.Collection>(),
                    publicLinkedType: Type<&SurferNFT.Collection>(),
                    createEmptyCollectionFunction: (fun(): @{NonFungibleToken.Collection} {
                        return <-SurferNFT.createEmptyCollection(nftType: Type<@SurferNFT.NFT>())
                    })
                )
            case Type<MetadataViews.NFTCollectionDisplay>():
                return MetadataViews.NFTCollectionDisplay(
                    name: "Wave OnFlow Surfers",
                    description: "Coleção de surfistas resgatados no bootcamp Wave OnFlow",
                    externalURL: MetadataViews.ExternalURL("https://flow.com"),
                    squareImage: MetadataViews.Media(
                        file: MetadataViews.HTTPFile(
                            url: "https://raw.githubusercontent.com/onflow/fcl-js/master/packages/fcl/assets/flow.png"
                        ),
                        mediaType: "image/png"
                    ),
                    bannerImage: MetadataViews.Media(
                        file: MetadataViews.HTTPFile(
                            url: "https://raw.githubusercontent.com/onflow/fcl-js/master/packages/fcl/assets/flow.png"
                        ),
                        mediaType: "image/png"
                    ),
                    socials: {}
                )
        }
        return nil
    }

    init() {
        self.CollectionStoragePath = /storage/SurferNFTCollection
        self.CollectionPublicPath = /public/SurferNFTCollection
        self.MinterStoragePath = /storage/SurferNFTMinter

        self.totalSupply = 0
        self.surfersRegistry = {}

        // Criar e salvar coleção
        let collection <- create Collection()
        self.account.storage.save(<-collection, to: self.CollectionStoragePath)

        let collectionCap = self.account.capabilities.storage.issue<&{SurferCollectionPublic}>(self.CollectionStoragePath)
        self.account.capabilities.publish(collectionCap, at: self.CollectionPublicPath)

        emit ContractInitialized()
    }
}