/**
 * FCL Client - Para usar no frontend, mas servido pela API
 */

import * as fcl from "https://unpkg.com/@onflow/fcl@1.4.0/dist/fcl.js";

class FlowClient {
    constructor() {
        this.user = null;
        this.apiBase = window.location.origin; // Usa mesma origem da API
        this.init();
    }

    async init() {
        // Busca config do backend
        const config = await fetch(`${this.apiBase}/api/fcl/config`).then(r => r.json());

        fcl.config()
            .put("accessNode.api", config.accessNode)
            .put("discovery.wallet", config.discovery)
            .put("flow.network", config.network)
            .put("app.detail.title", config.appDetails.title)
            .put("app.detail.icon", config.appDetails.icon);

        // Adiciona endereços dos contratos
        Object.entries(config.contracts).forEach(([name, address]) => {
            fcl.config().put(`0x${name}`, address);
        });
    }

    async connect() {
        this.user = await fcl.authenticate();

        // Notifica backend da autenticação
        await fetch(`${this.apiBase}/api/fcl/auth`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                address: this.user.addr,
                nonce: Date.now().toString(),
                signatures: [] // FCL forneceria as assinaturas reais
            })
        });

        return this.user;
    }

    async disconnect() {
        await fcl.unauthenticate();
        this.user = null;
    }

    async mintQuizPassNFT() {
        if (!this.user) throw new Error("Not connected");

        // Busca transação preparada do backend
        const txData = await fetch(
            `${this.apiBase}/api/fcl/transaction/mint-nft/${this.user.addr}`
        ).then(r => r.json());

        // Executa via FCL (usuário assina)
        const txId = await fcl.mutate({
            cadence: txData.cadence,
            args: (arg, t) => txData.args.map(a => arg(a.value, t[a.type])),
            proposer: fcl.authz,
            payer: fcl.authz,
            authorizations: [fcl.authz],
            limit: 999
        });

        // Aguarda confirmação
        return await fcl.tx(txId).onceSealed();
    }

    async submitQuizAnswers(answers) {
        if (!this.user) throw new Error("Not connected");

        // Backend prepara transação
        const txData = await fetch(`${this.apiBase}/api/fcl/transaction/quiz`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_address: this.user.addr,
                answers: answers
            })
        }).then(r => r.json());

        // Usuário assina e envia
        const txId = await fcl.mutate({
            cadence: txData.cadence,
            args: (arg, t) => txData.args.map(a => arg(a.value, t[a.type])),
            proposer: fcl.authz,
            payer: fcl.authz,
            authorizations: [fcl.authz]
        });

        return await fcl.tx(txId).onceSealed();
    }

    async getBalance(address) {
        const script = `
            import FlowToken from 0x7e60df042a9c0868
            import FungibleToken from 0x9a0766d93b6608b7

            pub fun main(address: Address): UFix64 {
                let account = getAccount(address)
                let vaultRef = account.getCapability(/public/flowTokenBalance)
                    .borrow<&FlowToken.Vault{FungibleToken.Balance}>()
                    ?? panic("Could not borrow Balance reference")

                return vaultRef.balance
            }
        `;

        const balance = await fcl.query({
            cadence: script,
            args: (arg, t) => [arg(address || this.user.addr, t.Address)]
        });

        return parseFloat(balance);
    }

    async checkHasNFT(address) {
        const script = `
            import QuizPassNFT from 0x01cf0e2f2f715450
            import NonFungibleToken from 0x631e88ae7f1d7c20

            pub fun main(address: Address): Bool {
                let account = getAccount(address)
                let collection = account
                    .getCapability(/public/QuizPassNFT)
                    .borrow<&{NonFungibleToken.CollectionPublic}>()

                if collection == nil {
                    return false
                }

                return collection!.getIDs().length > 0
            }
        `;

        return await fcl.query({
            cadence: script,
            args: (arg, t) => [arg(address || this.user.addr, t.Address)]
        });
    }

    // Monitora eventos em tempo real
    subscribeToEvents() {
        return fcl.events("A.01cf0e2f2f715450.QuizRace.QuizCompleted")
            .subscribe(event => {
                console.log("Quiz completado!", event);
                // Atualiza UI com vencedor
            });
    }
}

// Exporta cliente global
window.FlowClient = FlowClient;