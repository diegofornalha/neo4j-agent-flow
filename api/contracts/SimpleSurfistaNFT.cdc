import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

/// SimpleSurfistaNFT - NFT simplificada para surfistas
access(all) contract SimpleSurfistaNFT: NonFungibleToken {

    access(all) var totalSupply: UInt64
    access(all) var nomeRegistry: {String: UInt64}

    access(all) event ContractInitialized()
    access(all) event Withdraw(id: UInt64, from: Address?)
    access(all) event Deposit(id: UInt64, to: Address?)
    access(all) event SurfistaResgatado(id: UInt64, nome: String, address: Address)
    access(all) event FlowDepositado(id: UInt64, amount: UFix64)

    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath
    access(all) let MinterStoragePath: StoragePath

    /// NFT do Surfista Simplificada
    access(all) resource NFT: NonFungibleToken.INFT {
        access(all) let id: UInt64
        access(all) let nome: String
        access(all) let dataResgate: UFix64
        access(all) var flowBalance: UFix64  // Rastreia FLOW depositado

        init(id: UInt64, nome: String, flowInicial: UFix64) {
            self.id = id
            self.nome = nome
            self.dataResgate = getCurrentBlock().timestamp
            self.flowBalance = flowInicial
        }
    }

    /// Interface pública
    access(all) resource interface CollectionPublic {
        access(all) fun deposit(token: @NonFungibleToken.NFT)
        access(all) fun getIDs(): [UInt64]
        access(all) fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
    }

    /// Coleção de NFTs
    access(all) resource Collection: CollectionPublic, NonFungibleToken.Provider, NonFungibleToken.Receiver, NonFungibleToken.CollectionPublic {
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
            let token <- token as! @SimpleSurfistaNFT.NFT
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

        destroy() {
            destroy self.ownedNFTs
        }
    }

    access(all) fun createEmptyCollection(): @NonFungibleToken.Collection {
        return <- create Collection()
    }

    /// Resource de Minter
    access(all) resource NFTMinter {

        /// Minta uma NFT com débito de FLOW
        access(all) fun mintSurfista(
            nome: String,
            recipient: &{NonFungibleToken.CollectionPublic},
            flowAmount: UFix64
        ): UInt64 {
            let id = SimpleSurfistaNFT.totalSupply
            SimpleSurfistaNFT.totalSupply = SimpleSurfistaNFT.totalSupply + 1

            // Verificar nome único
            var nomeFinal = nome
            if SimpleSurfistaNFT.nomeRegistry[nome] != nil {
                let count = SimpleSurfistaNFT.nomeRegistry[nome]! + 1
                SimpleSurfistaNFT.nomeRegistry[nome] = count
                nomeFinal = nome.concat("#").concat(count.toString())
            } else {
                SimpleSurfistaNFT.nomeRegistry[nome] = 1
            }

            // Criar NFT com registro do FLOW
            let surfista <- create NFT(
                id: id,
                nome: nomeFinal,
                flowInicial: flowAmount
            )

            emit SurfistaResgatado(id: id, nome: nomeFinal, address: recipient.owner?.address ?? 0x0)
            emit FlowDepositado(id: id, amount: flowAmount)

            recipient.deposit(token: <-surfista)
            return id
        }
    }

    init() {
        self.totalSupply = 0
        self.nomeRegistry = {}

        self.CollectionStoragePath = /storage/simpleSurfistaNFTCollection
        self.CollectionPublicPath = /public/simpleSurfistaNFTCollection
        self.MinterStoragePath = /storage/simpleSurfistaNFTMinter

        // Criar o Minter
        let minter <- create NFTMinter()
        self.account.save(<-minter, to: self.MinterStoragePath)

        emit ContractInitialized()
    }
}