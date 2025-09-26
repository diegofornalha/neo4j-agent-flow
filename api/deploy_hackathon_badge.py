#!/usr/bin/env python3

import os
import subprocess
from flow_py_sdk import flow_client
from flow_py_sdk.signer import in_memory_signer
from flow_py_sdk.cadence import *
from flow_py_sdk import ProposalKey, Tx, TransactionStatus
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.testnet')

# Configuração
FLOW_ACCESS_NODE = "https://rest-testnet.onflow.org"
ACCOUNT_ADDRESS = "0x36395f9dde50ea27"
PRIVATE_KEY = os.getenv('FLOW_PRIVATE_KEY')

print(f"Deploy do contrato HackathonBadge")
print(f"Conta: {ACCOUNT_ADDRESS}")
print("=" * 50)

async def main():
    # Conectar ao cliente Flow
    async with flow_client(
        host=FLOW_ACCESS_NODE,
        port=443
    ) as client:
        # Ler contrato
        contract_path = Path("contracts/HackathonBadge.cdc")
        contract_code = contract_path.read_text()

        print(f"Lendo contrato de: {contract_path}")

        # Criar signer
        account_address = Address.from_hex(ACCOUNT_ADDRESS)
        signer = in_memory_signer.InMemorySigner(
            hash_algo=in_memory_signer.HashAlgo.SHA2_256,
            sign_algo=in_memory_signer.SignAlgo.ECDSA_secp256k1,
            private_key_hex=PRIVATE_KEY
        )

        # Obter informações da conta
        account = await client.get_account(address=account_address.bytes)

        # Criar transaction
        update_contract_tx = (
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
        update_contract_tx = await signer.sign_transaction(
            transaction=update_contract_tx,
            account_address=account_address
        )

        result = await client.send_transaction(transaction=update_contract_tx)
        tx_id = result.id.hex()

        print(f"\nTransação enviada: {tx_id}")
        print(f"Aguardando confirmação...")

        # Aguardar resultado
        tx_result = await client.get_transaction_result(id=result.id)

        if tx_result.status == TransactionStatus.SEALED:
            print(f"✅ Contrato HackathonBadge atualizado com sucesso!")
            print(f"Ver no Flowscan: https://testnet.flowscan.io/transaction/{tx_id}")

            # Verificar se aparece no Flowscan
            print(f"\n📦 Verificar NFTs no Flowscan:")
            print(f"https://testnet.flowscan.io/nft/A.{ACCOUNT_ADDRESS[2:]}.HackathonBadge.NFT")
        else:
            print(f"❌ Erro na transação: {tx_result.error_message}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())