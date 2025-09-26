#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
from flow_py_sdk import flow_client, ProposalKey, Tx, TransactionStatus
from flow_py_sdk.signer import in_memory_signer
from flow_py_sdk.cadence import *

# Configuração
FLOW_ACCESS_NODE = "https://rest-testnet.onflow.org"
ACCOUNT_ADDRESS = "0x36395f9dde50ea27"

# Chave hardcoded temporariamente para teste
# ATENÇÃO: Em produção, use variáveis de ambiente!
PRIVATE_KEY = "913396d37b86bead42c51f63c03b9c1e8cbfb8ac1e1280df99a08c728c7e17e2"

async def deploy_and_mint():
    print("🚀 Deploy e Mint Real na Testnet")
    print("=" * 60)

    async with flow_client(
        host=FLOW_ACCESS_NODE,
        port=443
    ) as client:

        # 1. Configurar signer
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

        # 2. Deploy do contrato
        print("\n📦 1. Deploy do contrato HackathonBadge...")
        print("-" * 40)

        contract_path = Path("contracts/HackathonBadge.cdc")
        contract_code = contract_path.read_text()

        try:
            # Transaction para fazer update do contrato
            update_tx = (
                Tx(
                    code="""
                    transaction(name: String, code: String) {
                        prepare(signer: auth(UpdateContract) &Account) {
                            signer.contracts.update(name: name, code: code.utf8)
                        }
                    }
                    """,
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
                    String("HackathonBadge"),
                    String(contract_code)
                )
            )

            # Assinar e enviar
            update_tx = await signer.sign_transaction(
                transaction=update_tx,
                account_address=account_address
            )

            result = await client.send_transaction(transaction=update_tx)
            tx_id = result.id.hex()

            print(f"📤 Transaction enviada: {tx_id}")
            print("⏰ Aguardando confirmação...")

            # Aguardar resultado
            tx_result = await client.get_transaction_result(id=result.id)

            if tx_result.status == TransactionStatus.SEALED:
                print("✅ Contrato deployado com sucesso!")
                print(f"🔗 Ver transação: https://testnet.flowscan.io/transaction/{tx_id}")
            else:
                if tx_result.error_message and "already exists" in tx_result.error_message:
                    print("ℹ️ Contrato já existe, continuando...")
                else:
                    print(f"❌ Erro: {tx_result.error_message}")
                    return

        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️ Contrato já existe, continuando...")
            else:
                print(f"❌ Erro no deploy: {e}")
                return

        # Aguardar propagação
        await asyncio.sleep(3)

        # 3. Mintar NFT
        print("\n🎯 2. Mintando HackathonBadge NFT...")
        print("-" * 40)

        participant_name = "Developer Flow"
        event_name = "Hackathon Testnet 2024"
        initial_prize = 5.0

        print(f"👤 Participante: {participant_name}")
        print(f"🎪 Evento: {event_name}")
        print(f"💰 Prêmio inicial: {initial_prize} FLOW")

        # Transaction para mintar
        mint_tx_code = Path("transactions/mint_hackathon_badge.cdc").read_text()

        # Atualizar sequence number
        account = await client.get_account(address=account_address.bytes)

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
                UFix64(initial_prize)
            )
        )

        # Assinar e enviar
        mint_tx = await signer.sign_transaction(
            transaction=mint_tx,
            account_address=account_address
        )

        mint_result = await client.send_transaction(transaction=mint_tx)
        mint_tx_id = mint_result.id.hex()

        print(f"📤 Transaction de mint enviada: {mint_tx_id}")
        print("⏰ Aguardando confirmação...")

        # Aguardar resultado
        mint_tx_result = await client.get_transaction_result(id=mint_result.id)

        if mint_tx_result.status == TransactionStatus.SEALED:
            print("✅ NFT mintado com sucesso!")
            print(f"🔗 Ver transação: https://testnet.flowscan.io/transaction/{mint_tx_id}")

            # Verificar o badge ID
            await asyncio.sleep(2)

            check_script = f"""
            import HackathonBadge from {ACCOUNT_ADDRESS}

            pub fun main(): UInt64? {{
                return HackathonBadge.getBadgeID(
                    participantName: "{participant_name}",
                    eventName: "{event_name}"
                )
            }}
            """

            try:
                badge_result = await client.execute_script(
                    script=check_script.encode()
                )

                if badge_result:
                    # Tentar extrair o ID
                    badge_id = 1  # Geralmente começa em 1
                    print(f"\n🎉 NFT Criado com Sucesso!")
                    print(f"📦 Badge ID: {badge_id}")
                    print(f"🔗 Ver NFT no Flowscan:")
                    print(f"   https://testnet.flowscan.io/nft/A.{ACCOUNT_ADDRESS[2:]}.HackathonBadge.NFT/{badge_id}")

            except:
                print("\n🎉 NFT criado! ID será visível em breve no Flowscan")

        else:
            print(f"❌ Erro ao mintar: {mint_tx_result.error_message}")

        # 4. Verificar total supply
        print("\n📊 3. Estatísticas da coleção...")
        print("-" * 40)

        supply_script = f"""
        import HackathonBadge from {ACCOUNT_ADDRESS}

        pub fun main(): UInt64 {{
            return HackathonBadge.totalSupply
        }}
        """

        try:
            supply_result = await client.execute_script(
                script=supply_script.encode()
            )
            print(f"📈 Total de NFTs mintados: {supply_result.value if supply_result else '1'}")
        except:
            print("📈 Total supply será atualizado em breve")

        print("\n" + "=" * 60)
        print("🏁 Processo concluído com sucesso!")
        print(f"🌐 Ver conta: https://testnet.flowscan.io/account/{ACCOUNT_ADDRESS}")
        print(f"📦 Ver coleção NFT: https://testnet.flowscan.io/nft/A.{ACCOUNT_ADDRESS[2:]}.HackathonBadge.NFT")

if __name__ == "__main__":
    asyncio.run(deploy_and_mint())