#!/usr/bin/env python3
"""
Verifica o saldo Flow usando MCP tools
"""

import json
import os
import sys
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

async def check_balance_with_mcp(address=None, network=None):
    """Usa o Flow MCP para verificar o saldo real na blockchain"""

    # Permite passar endereço como argumento ou usar da env
    if not address:
        address = os.getenv('FLOW_ACCOUNT_ADDRESS')

    # Permite passar network como argumento ou usar da env
    if not network:
        network = os.getenv('FLOW_NETWORK', 'mainnet')

    # Remove prefixo 0x se presente e padroniza
    if address and address.startswith('0x'):
        address = address[2:]

    # Validação básica
    if not address:
        print("❌ Erro: Endereço Flow não fornecido!")
        print("Use: python3 check_flow_balance_mcp.py <endereço> [network]")
        return

    print("=" * 60)
    print("💰 VERIFICANDO SALDO FLOW NA BLOCKCHAIN")
    print("=" * 60)
    print(f"\n📍 Endereço: 0x{address}")
    print(f"🌐 Rede: {network}")
    print("-" * 60)

    import subprocess

    # Seleciona API baseada na network
    api_urls = {
        'mainnet': 'https://rest-mainnet.onflow.org',
        'testnet': 'https://rest-testnet.onflow.org',
        'emulator': 'http://localhost:8888'
    }

    api_url = api_urls.get(network, api_urls['mainnet'])

    # Query para obter informações da conta
    query = f"""
    curl -s -X GET "{api_url}/v1/accounts/{address}?expand=contracts,keys" \
    -H "Content-Type: application/json"
    """

    try:
        result = subprocess.run(query, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                print(f"\u274c Erro ao decodificar resposta JSON")
                print(f"Resposta: {result.stdout[:500]}")
                return

            # Extrai o saldo
            balance = data.get('balance', '0')

            # Converte de microFLOW para FLOW (divide por 10^8)
            flow_balance = int(balance) / 100_000_000

            print(f"\n💎 INFORMAÇÕES DA CONTA:")
            print(f"✅ Endereço: 0x{data.get('address')}")
            print(f"💰 Saldo: {flow_balance:.8f} FLOW")

            # Mostra em formato mais legível para valores grandes
            if flow_balance >= 1:
                print(f"   ({flow_balance:,.2f} FLOW)")

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
                print(f"🎯 Você tem {flow_balance:,.2f} FLOW disponíveis!")
            else:
                print("⚠️ Conta sem saldo.")
                if network == 'testnet':
                    print("🔗 Solicite FLOW no faucet: https://testnet-faucet.onflow.org/")

        else:
            print(f"❌ Erro ao consultar: {result.stderr}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    print("=" * 60)

if __name__ == "__main__":
    # Permite passar endereço e network como argumentos
    address = sys.argv[1] if len(sys.argv) > 1 else None
    network = sys.argv[2] if len(sys.argv) > 2 else None

    asyncio.run(check_balance_with_mcp(address, network))