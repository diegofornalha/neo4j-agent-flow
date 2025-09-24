#!/usr/bin/env python3
"""
Verifica o saldo Flow usando MCP tools
"""

import json
import os
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

async def check_balance_with_mcp():
    """Usa o Flow MCP para verificar o saldo real na blockchain"""

    address = os.getenv('FLOW_ACCOUNT_ADDRESS')
    network = os.getenv('FLOW_NETWORK', 'testnet')

    print("=" * 60)
    print("💰 VERIFICANDO SALDO FLOW NA BLOCKCHAIN")
    print("=" * 60)
    print(f"\n📍 Endereço: {address}")
    print(f"🌐 Rede: {network}")
    print("-" * 60)

    # Simulação de chamada MCP (normalmente seria via SDK)
    # Na prática, o MCP está integrado no servidor

    import subprocess

    # Comando para verificar saldo usando curl direto na API Flow
    testnet_api = "https://rest-testnet.onflow.org"

    # Query para obter informações da conta
    query = f"""
    curl -s -X GET "{testnet_api}/v1/accounts/{address}?expand=contracts,keys" \
    -H "Content-Type: application/json"
    """

    try:
        result = subprocess.run(query, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            data = json.loads(result.stdout)

            # Extrai o saldo
            balance = data.get('balance', '0')

            # Converte de microFLOW para FLOW (divide por 10^8)
            flow_balance = int(balance) / 100_000_000

            print(f"\n💎 INFORMAÇÕES DA CONTA:")
            print(f"✅ Endereço: {data.get('address')}")
            print(f"💰 Saldo: {flow_balance:.2f} FLOW")

            # Informações adicionais
            contracts = data.get('contracts', {})
            keys = data.get('keys', [])

            if contracts:
                print(f"📜 Contratos: {len(contracts)}")
                for name in contracts.keys():
                    print(f"   - {name}")

            if keys:
                print(f"🔑 Chaves: {len(keys)}")
                for key in keys:
                    print(f"   - Index: {key.get('index')} | Weight: {key.get('weight')}")

            # Verifica capacidade de storage
            storage_capacity = int(data.get('storage_capacity', 0)) / 100_000_000
            storage_used = int(data.get('storage_used', 0))

            print(f"\n💾 STORAGE:")
            print(f"   Capacidade: {storage_capacity:.2f} MB")
            print(f"   Usado: {storage_used} bytes")

            print("\n" + "=" * 60)

            if flow_balance > 0:
                print("✅ CONTA ATIVA E COM SALDO!")
                print(f"🎯 Você tem {flow_balance:.2f} FLOW disponíveis para o hackathon!")
            else:
                print("⚠️ Conta sem saldo. Solicite FLOW no faucet:")
                print("🔗 https://testnet-faucet.onflow.org/")

        else:
            print(f"❌ Erro ao consultar: {result.stderr}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_balance_with_mcp())