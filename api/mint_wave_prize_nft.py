#!/usr/bin/env python3

import asyncio
from flow_py_sdk import flow_client, ProposalKey, Tx, TransactionStatus
from flow_py_sdk.signer import in_memory_signer
from flow_py_sdk.cadence import *
from pathlib import Path

# Configuração
FLOW_ACCESS_NODE = "https://rest-testnet.onflow.org"
ACCOUNT_ADDRESS = "0x36395f9dde50ea27"

# Chave para teste - Em produção use variáveis de ambiente!
PRIVATE_KEY = "913396d37b86bead42c51f63c03b9c1e8cbfb8ac1e1280df99a08c728c7e17e2"

async def mint_wave_nft():
    print("🚀 Mintando WaveEventPrizeNFT Real na Testnet")
    print("=" * 60)

    async with flow_client(
        host=FLOW_ACCESS_NODE,
        port=443
    ) as client:

        # Configurar signer
        account_address = Address.from_hex(ACCOUNT_ADDRESS)
        signer = in_memory_signer.InMemorySigner(
            hash_algo=in_memory_signer.HashAlgo.SHA2_256,
            sign_algo=in_memory_signer.SignAlgo.ECDSA_secp256k1,
            private_key_hex=PRIVATE_KEY
        )

        # Obter informações da conta
        account = await client.get_account(address=account_address.bytes)
        print(f"📍 Conta: {ACCOUNT_ADDRESS}")
        print(f"💰 Saldo: {float(account.balance) / 1e8} FLOW")

        # Parâmetros para o NFT
        participant_name = "João Silva Real"
        event_name = "Flow Testnet Hackathon 2024"
        registration_fee = 1.0
        initial_prize = 10.0

        print(f"\n🎯 Mintando NFT...")
        print("-" * 40)
        print(f"👤 Participante: {participant_name}")
        print(f"🎪 Evento: {event_name}")
        print(f"💵 Taxa: {registration_fee} FLOW")
        print(f"💰 Prêmio inicial: {initial_prize} FLOW")

        # Transaction para registrar com prêmio
        mint_tx_code = """
        import WaveEventPrizeNFT from 0x36395f9dde50ea27
        import FlowToken from 0x7e60df042a9c0868
        import FungibleToken from 0x9a0766d93b6608b7
        import NonFungibleToken from 0x631e88ae7f1d7c20

        transaction(participantName: String, eventName: String, registrationFee: UFix64, initialPrize: UFix64) {
            let collection: &{NonFungibleToken.Receiver}
            let paymentVault: @FlowToken.Vault
            let prizeVault: @FlowToken.Vault?

            prepare(signer: auth(Storage, Capabilities) &Account) {
                // Verifica se tem coleção, senão cria
                if signer.storage.type(at: WaveEventPrizeNFT.CollectionStoragePath) == nil {
                    let collection <- WaveEventPrizeNFT.createEmptyCollection()
                    signer.storage.save(<-collection, to: WaveEventPrizeNFT.CollectionStoragePath)

                    let cap = signer.capabilities.storage.issue<&WaveEventPrizeNFT.Collection>(
                        WaveEventPrizeNFT.CollectionStoragePath
                    )
                    signer.capabilities.publish(cap, at: WaveEventPrizeNFT.CollectionPublicPath)
                }

                // Pega a coleção
                let cap = signer.capabilities.get<&{NonFungibleToken.Receiver}>(
                    WaveEventPrizeNFT.CollectionPublicPath
                )
                self.collection = cap.borrow() ?? panic("Não foi possível pegar a coleção")

                // Pega o vault de Flow
                let vaultRef = signer.storage
                    .borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(from: /storage/flowTokenVault)
                    ?? panic("Vault de Flow não encontrado")

                // Retira pagamento e prêmio inicial
                self.paymentVault <- vaultRef.withdraw(amount: registrationFee) as! @FlowToken.Vault

                if initialPrize > 0.0 {
                    self.prizeVault <- vaultRef.withdraw(amount: initialPrize) as! @FlowToken.Vault
                } else {
                    self.prizeVault <- nil
                }
            }

            execute {
                // Registra participante com prêmio inicial
                WaveEventPrizeNFT.registerParticipantWithPrize(
                    participantName: participantName,
                    eventName: eventName,
                    recipient: self.collection,
                    payment: <-self.paymentVault,
                    initialPrize: <-self.prizeVault
                )

                log("✅ NFT mintado com sucesso!")
                log("Participante: ".concat(participantName))
                log("Evento: ".concat(eventName))
                log("Prêmio inicial: ".concat(initialPrize.toString()).concat(" FLOW"))
            }
        }
        """

        mint_tx = (
            Tx(
                code=mint_tx_code,
                reference_block_id=await client.get_latest_block_id(),
                payer=account_address,
                proposal_key=ProposalKey(
                    key_address=account_address,
                    key_id=0,
                    key_sequence_number=account.keys[0].sequence_number
                )
            )
            .add_authorizers(account_address)
            .add_arguments(
                String(participant_name),
                String(event_name),
                UFix64(registration_fee),
                UFix64(initial_prize)
            )
        )

        # Assinar e enviar
        mint_tx = await signer.sign_transaction(
            transaction=mint_tx,
            account_address=account_address
        )

        result = await client.send_transaction(transaction=mint_tx)
        tx_id = result.id.hex()

        print(f"\n📤 Transaction enviada: {tx_id}")
        print("⏰ Aguardando confirmação...")

        # Aguardar resultado
        tx_result = await client.get_transaction_result(id=result.id)

        if tx_result.status == TransactionStatus.SEALED:
            print("\n🎉 NFT Mintado com Sucesso!")
            print("-" * 40)
            print(f"✅ Participante: {participant_name}")
            print(f"✅ Evento: {event_name}")
            print(f"✅ Prêmio: {initial_prize} FLOW")
            print(f"\n🔗 Ver transação:")
            print(f"   https://testnet.flowscan.io/transaction/{tx_id}")

            # Verificar o ID do participante
            await asyncio.sleep(3)

            check_script = f"""
            import WaveEventPrizeNFT from 0x36395f9dde50ea27

            pub fun main(): UInt64? {{
                return WaveEventPrizeNFT.getParticipantID(
                    name: "{participant_name}",
                    event: "{event_name}"
                )
            }}
            """

            try:
                id_result = await client.execute_script(
                    script=check_script.encode()
                )

                if id_result and hasattr(id_result, 'value'):
                    nft_id = id_result.value
                    print(f"\n📦 NFT ID: {nft_id}")
                    print(f"🔗 Ver NFT no Flowscan:")
                    print(f"   https://testnet.flowscan.io/nft/A.{ACCOUNT_ADDRESS[2:]}.WaveEventPrizeNFT.NFT/{nft_id}")
                else:
                    print(f"\n📦 NFT criado! ID: Geralmente começa em 1")
                    print(f"🔗 Ver coleção NFT:")
                    print(f"   https://testnet.flowscan.io/nft/A.{ACCOUNT_ADDRESS[2:]}.WaveEventPrizeNFT.NFT")

            except Exception as e:
                print(f"\n📦 NFT criado com sucesso!")
                print(f"🔗 Ver coleção:")
                print(f"   https://testnet.flowscan.io/account/{ACCOUNT_ADDRESS}/collection/A.{ACCOUNT_ADDRESS[2:]}.WaveEventPrizeNFT.Collection")

        else:
            print(f"\n❌ Erro ao mintar: {tx_result.error_message}")

        # Verificar total de participantes
        print("\n📊 Estatísticas do Evento")
        print("-" * 40)

        stats_script = f"""
        import WaveEventPrizeNFT from 0x36395f9dde50ea27

        pub fun main(eventName: String): UInt64 {{
            let participants = WaveEventPrizeNFT.getEventParticipants(event: eventName)
            return UInt64(participants.length)
        }}
        """

        try:
            stats_result = await client.execute_script(
                script=stats_script.encode(),
                arguments=[String(event_name)]
            )

            if stats_result:
                print(f"👥 Total de participantes no evento: {stats_result.value if hasattr(stats_result, 'value') else '1'}")
        except:
            print("👥 Estatísticas serão atualizadas em breve")

        print("\n" + "=" * 60)
        print("🏁 Processo concluído!")
        print(f"🌐 Ver conta: https://testnet.flowscan.io/account/{ACCOUNT_ADDRESS}")

if __name__ == "__main__":
    asyncio.run(mint_wave_nft())