import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// WaveNFT - Sistema simplificado de NFTs para nomes
access(all) contract WaveNFT: NonFungibleToken {

    /// Eventos
    access(all) event ContractInitialized()
    access(all) event Withdraw(id: UInt64, from: Address?)
    access(all) event Deposit(id: UInt64, to: Address?)
    access(all) event NameMinted(id: UInt64, name: String, owner: Address)

    /// Paths
    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath

    /// Total de NFTs
    access(all) var totalSupply: UInt64

    /// Mapeamento de nomes
    access(contract) var nameToID: {String: UInt64}

    /// Preço base
    access(all) var basePrice: UFix64

    /// NFT simples
    access(all) resource NFT: NonFungibleToken.NFT {
        access(all) let id: UInt64
        access(all) let name: String
        access(all) let mintedAt: UFix64

        init(name: String) {
            self.id = WaveNFT.totalSupply
            self.name = name
            self.mintedAt = getCurrentBlock().timestamp

            WaveNFT.totalSupply = WaveNFT.totalSupply + 1
            WaveNFT.nameToID[name] = self.id
        }

        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <- WaveNFT.createEmptyCollection()
        }

        access(all) view fun getViews(): [Type] {
            return [Type<MetadataViews.Display>()]
        }

        access(all) fun resolveView(_ view: Type): AnyStruct? {
            switch view {
                case Type<MetadataViews.Display>():
                    return MetadataViews.Display(
                        name: self.name,
                        description: "Wave Name NFT: ".concat(self.name),
                        thumbnail: MetadataViews.HTTPFile(url: "")
                    )
            }
            return nil
        }
    }

    /// Coleção simples
    access(all) resource Collection: NonFungibleToken.Collection {
        access(all) var ownedNFTs: @{UInt64: {NonFungibleToken.NFT}}

        init() {
            self.ownedNFTs <- {}
        }

        access(all) fun getSupportedNFTTypes(): {Type: Bool} {
            return {Type<@WaveNFT.NFT>(): true}
        }

        access(all) fun isSupportedNFTType(type: Type): Bool {
            return type == Type<@WaveNFT.NFT>()
        }

        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <- create Collection()
        }

        access(all) view fun getLength(): Int {
            return self.ownedNFTs.length
        }

        access(all) fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        access(NonFungibleToken.Withdraw) fun withdraw(withdrawID: UInt64): @{NonFungibleToken.NFT} {
            let token <- self.ownedNFTs.remove(key: withdrawID)
                ?? panic("NFT não existe")

            emit Withdraw(id: token.id, from: self.owner?.address)
            return <-token
        }

        access(all) fun deposit(token: @{NonFungibleToken.NFT}) {
            let token <- token as! @WaveNFT.NFT
            let id: UInt64 = token.id

            let oldToken <- self.ownedNFTs[id] <- token
            destroy oldToken

            emit Deposit(id: id, to: self.owner?.address)
        }

        access(all) view fun borrowNFT(_ id: UInt64): &{NonFungibleToken.NFT}? {
            return &self.ownedNFTs[id] as &{NonFungibleToken.NFT}?
        }

        access(all) fun borrowWaveNFT(id: UInt64): &WaveNFT.NFT? {
            if self.ownedNFTs[id] != nil {
                let ref = (&self.ownedNFTs[id] as &{NonFungibleToken.NFT}?)!
                return ref as! &WaveNFT.NFT
            }
            return nil
        }
    }

    /// Minter público
    access(all) fun mintNFT(name: String, recipient: &{NonFungibleToken.Receiver}, payment: @FlowToken.Vault) {
        pre {
            WaveNFT.nameToID[name] == nil: "Nome já existe!"
            payment.balance >= WaveNFT.calculatePrice(name): "Pagamento insuficiente"
        }

        destroy payment

        let nft <- create NFT(name: name)
        let id = nft.id
        recipient.deposit(token: <-nft)

        emit NameMinted(id: id, name: name, owner: recipient.owner?.address ?? panic("Sem owner"))
    }

    /// Calcula preço
    access(all) view fun calculatePrice(_ name: String): UFix64 {
        let length = name.length

        if length <= 3 {
            return self.basePrice * 100.0
        } else if length <= 5 {
            return self.basePrice * 10.0
        } else if length <= 8 {
            return self.basePrice * 5.0
        }

        return self.basePrice
    }

    /// Verifica se nome existe
    access(all) view fun nameExists(_ name: String): Bool {
        return self.nameToID[name] != nil
    }

    /// Cria coleção vazia
    access(all) fun createEmptyCollection(nftType: Type): @{NonFungibleToken.Collection} {
        return <- create Collection()
    }

    /// Cria coleção vazia (compatibilidade)
    access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
        return <- create Collection()
    }

    init() {
        self.CollectionStoragePath = /storage/waveNFTCollection
        self.CollectionPublicPath = /public/waveNFTCollection

        self.totalSupply = 0
        self.nameToID = {}
        self.basePrice = 1.0

        emit ContractInitialized()
    }
}