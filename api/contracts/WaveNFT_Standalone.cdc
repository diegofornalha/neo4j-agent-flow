import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// WaveNFT - Sistema de nomes como NFTs sem herdar NonFungibleToken
/// Cada nome registrado é um NFT único e transferível
access(all) contract WaveNFT {

    /// Eventos
    access(all) event ContractInitialized()
    access(all) event NameMinted(id: UInt64, name: String, owner: Address)
    access(all) event NameTransferred(id: UInt64, from: Address?, to: Address?)
    access(all) event NameBurned(id: UInt64, name: String)

    /// Paths de storage
    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath

    /// Contador de NFTs
    access(all) var totalSupply: UInt64

    /// Mapeamento de nomes para IDs
    access(contract) var nameToID: {String: UInt64}

    /// Preço base para registro
    access(all) var basePrice: UFix64

    /// NFT que representa um nome
    access(all) resource NFT {
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

        /// Retorna os dados do NFT
        access(all) view fun getMetadata(): {String: AnyStruct} {
            return {
                "id": self.id,
                "name": self.name,
                "mintedAt": self.mintedAt,
                "originalOwner": self.originalOwner
            }
        }
    }

    /// Interface pública da coleção
    access(all) resource interface CollectionPublic {
        access(all) fun getIDs(): [UInt64]
        access(all) fun borrowNFT(id: UInt64): &NFT?
        access(all) fun deposit(token: @NFT)
    }

    /// Coleção de NFTs
    access(all) resource Collection: CollectionPublic {
        access(all) var ownedNFTs: @{UInt64: NFT}

        init() {
            self.ownedNFTs <- {}
        }

        /// Retira um NFT da coleção
        access(all) fun withdraw(withdrawID: UInt64): @NFT {
            let token <- self.ownedNFTs.remove(key: withdrawID)
                ?? panic("NFT não existe na coleção")

            emit NameTransferred(id: token.id, from: self.owner?.address, to: nil)
            return <-token
        }

        /// Deposita um NFT na coleção
        access(all) fun deposit(token: @NFT) {
            let id: UInt64 = token.id

            let oldToken <- self.ownedNFTs[id] <- token
            destroy oldToken

            emit NameTransferred(id: id, from: nil, to: self.owner?.address)
        }

        /// Retorna lista de IDs na coleção
        access(all) fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        /// Pega referência de um NFT
        access(all) fun borrowNFT(id: UInt64): &NFT? {
            return &self.ownedNFTs[id] as &NFT?
        }

        /// Queima um NFT
        access(all) fun burn(id: UInt64) {
            let token <- self.ownedNFTs.remove(key: id)
                ?? panic("NFT não existe")

            let name = token.name
            WaveNFT.nameToID.remove(key: name)
            destroy token

            emit NameBurned(id: id, name: name)
        }
    }

    /// Minta um novo nome NFT
    access(all) fun mintNFT(
        name: String,
        recipient: &Collection,
        payment: @FlowToken.Vault
    ) {
        pre {
            WaveNFT.nameToID[name] == nil: "Nome já existe!"
            payment.balance >= WaveNFT.calculatePrice(name): "Pagamento insuficiente"
        }

        // Destruir pagamento
        destroy payment

        let owner = recipient.owner?.address ?? panic("Recipient sem owner")

        // Criar novo NFT
        let nft <- create NFT(name: name, owner: owner)
        let id = nft.id

        // Depositar na coleção
        recipient.deposit(token: <-nft)

        emit NameMinted(id: id, name: name, owner: owner)
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
    access(all) view fun nameExists(_ name: String): Bool {
        return self.nameToID[name] != nil
    }

    /// Retorna o ID de um nome
    access(all) view fun getNameID(_ name: String): UInt64? {
        return self.nameToID[name]
    }

    /// Retorna todos os nomes registrados
    access(all) view fun getAllNames(): [String] {
        return self.nameToID.keys
    }

    /// Cria uma coleção vazia
    access(all) fun createEmptyCollection(): @Collection {
        return <- create Collection()
    }

    init() {
        // Inicializar paths
        self.CollectionStoragePath = /storage/waveNFTCollection
        self.CollectionPublicPath = /public/waveNFTCollection

        // Inicializar variáveis
        self.totalSupply = 0
        self.nameToID = {}
        self.basePrice = 1.0  // 1 FLOW base

        emit ContractInitialized()
    }
}