#!/usr/bin/env python3
"""
Script para testar diferentes métodos de registro FIND
Vamos tentar várias abordagens assim que tivermos novas informações
"""

import asyncio
from flow_py_sdk import flow_client, Tx, ProposalKey
from flow_py_sdk.signer import in_memory_signer
from flow_py_sdk.cadence import Address
import json

# Configurações
ACCOUNT = '0x36395f9dde50ea27'
PRIVATE_KEY = '7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3'
FIND_CONTRACT = '0x35717efbbce11c74'

async def test_method(transaction_code: str, description: str):
    """Testa um método de registro FIND"""
    print(f"\n🧪 Testando: {description}")
    print("=" * 50)

    async with flow_client(host='https://rest-testnet.onflow.org') as client:
        try:
            # Buscar conta
            address_bytes = bytes.fromhex(ACCOUNT.replace('0x', ''))
            account = await client.get_account(address=address_bytes)

            # Preparar transação
            latest_block = await client.get_latest_block()

            tx = Tx(
                code=transaction_code,
                reference_block_id=latest_block.id,
                payer=Address.from_hex(ACCOUNT),
                proposer=Address.from_hex(ACCOUNT),
                authorizers=[Address.from_hex(ACCOUNT)],
                proposal_key=ProposalKey(
                    key_address=Address.from_hex(ACCOUNT),
                    key_index=0,
                    key_sequence_number=account.keys[0].sequence_number
                ),
                gas_limit=100
            )

            # Assinar
            signer = in_memory_signer.InMemorySigner(
                hash_algo=in_memory_signer.HashAlgo.SHA2_256,
                sign_algo=in_memory_signer.SignAlgo.ECDSA_secp256k1,
                private_key_hex=PRIVATE_KEY
            )

            tx.add_envelope_signature(
                signer_address=Address.from_hex(ACCOUNT),
                signer_key_index=0,
                signer=signer
            )

            # Enviar
            result = await client.send_transaction(transaction=tx)
            tx_id = result.id.hex()
            print(f"✅ Transação enviada: {tx_id}")

            # Aguardar
            await client.wait_for_transaction(tx_id)
            tx_result = await client.get_transaction_result(tx_id)

            print(f"📊 Status: {tx_result.status.name}")
            print(f"🔗 https://testnet.flowscan.io/transaction/{tx_id}")

            if tx_result.error_message:
                print(f"❌ Erro: {tx_result.error_message}")
            else:
                print("✨ Sucesso!")

            return tx_result.status.name == "SEALED" and not tx_result.error_message

        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

# Métodos para testar quando tivermos novas informações
METHODS_TO_TEST = {
    "method_1": {
        "description": "Tentativa com public fun register",
        "code": f"""
import FIND from {FIND_CONTRACT}

transaction(name: String) {{
    prepare(account: auth(Storage) &Account) {{
        // Aguardando nova sintaxe descoberta
        log("Testando registro: ".concat(name))
    }}
}}
"""
    },
    # Adicionar mais métodos conforme descobrirmos
}

async def main():
    print("🔍 FIND Registration Test Suite")
    print("💰 Conta: " + ACCOUNT)
    print("📝 Pronto para testar novos métodos assim que descobrirmos!")
    print("\nAguardando novas informações sobre:")
    print("- APIs REST do FIND")
    print("- Métodos públicos atualizados")
    print("- Contratos wrapper/proxy")
    print("- Soluções da comunidade")

    # Quando tivermos métodos, descomentar:
    # for method_name, method_info in METHODS_TO_TEST.items():
    #     success = await test_method(
    #         method_info["code"],
    #         method_info["description"]
    #     )
    #     if success:
    #         print(f"🎉 MÉTODO FUNCIONOU: {method_name}")
    #         break

if __name__ == "__main__":
    asyncio.run(main())