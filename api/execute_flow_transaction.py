#!/usr/bin/env python3
"""
Executa uma transação simples na Flow Testnet
Usando a conta 0x36395f9dde50ea27 com 101,000 FLOW
"""

import asyncio
import time
from flow_py_sdk import flow_client, ProposalKey, Tx
from flow_py_sdk.signer import in_memory_signer
from flow_py_sdk.cadence import Address

async def main():
    # Configurações
    account_address = '0x36395f9dde50ea27'
    private_key_hex = '7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3'

    print('🚀 Executando transação na Flow Testnet')
    print('=' * 50)
    print(f'📍 Conta: {account_address}')

    # Cliente REST API
    async with flow_client(
        host='https://rest-testnet.onflow.org'
    ) as client:

        # Buscar informações da conta
        address_bytes = bytes.fromhex(account_address.replace('0x', ''))
        account = await client.get_account(address=address_bytes)
        print(f'💰 Saldo: {account.balance / 100000000:.2f} FLOW')
        print(f'🔄 Sequence: {account.keys[0].sequence_number}')

        # Timestamp único
        timestamp = int(time.time())

        # Transação simples
        transaction_script = f'''
        transaction {{
            prepare(signer: auth(Storage) &Account) {{
                log("🎯 Transação executada com sucesso!")
                log("⏰ Unix timestamp: {timestamp}")
                log("📅 Data: 2025-01-25")
                log("🔑 Conta: ".concat(signer.address.toString()))
            }}
        }}
        '''

        # Obter bloco mais recente
        latest_block = await client.get_latest_block()

        # Criar transação
        tx = Tx(
            code=transaction_script,
            reference_block_id=latest_block.id,
            payer=Address.from_hex(account_address),
            proposer=Address.from_hex(account_address),
            authorizers=[Address.from_hex(account_address)],
            proposal_key=ProposalKey(
                key_address=Address.from_hex(account_address),
                key_index=0,
                key_sequence_number=account.keys[0].sequence_number
            ),
            gas_limit=100
        )

        # Assinar
        signer = in_memory_signer.InMemorySigner(
            hash_algo=in_memory_signer.HashAlgo.SHA2_256,
            sign_algo=in_memory_signer.SignAlgo.ECDSA_secp256k1,
            private_key_hex=private_key_hex
        )

        tx.add_envelope_signature(
            signer_address=Address.from_hex(account_address),
            signer_key_index=0,
            signer=signer
        )

        # Enviar
        print('\n📤 Enviando transação...')
        result = await client.send_transaction(transaction=tx)
        tx_id = result.id.hex()
        print(f'✅ ID: {tx_id}')

        # Aguardar confirmação
        print('⏳ Aguardando confirmação...')
        await client.wait_for_transaction(tx_id)
        tx_result = await client.get_transaction_result(tx_id)

        print(f'\n🎉 TRANSAÇÃO CONFIRMADA!')
        print(f'📊 Status: {tx_result.status.name}')
        print(f'🔗 Ver no Flowscan:')
        print(f'   https://testnet.flowscan.io/transaction/{tx_id}')

        # Saldo atualizado
        account_updated = await client.get_account(address=address_bytes)
        print(f'\n💰 Saldo final: {account_updated.balance / 100000000:.2f} FLOW')
        print(f'⛽ Taxa estimada: 0.00001 FLOW')

if __name__ == '__main__':
    asyncio.run(main())