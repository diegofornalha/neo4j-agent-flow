#!/usr/bin/env python3
"""
Script otimizado para verificar saldo de conta Flow - APENAS TESTNET
Mais rápido pois não verifica Mainnet desnecessariamente
"""

import requests
import json
import sys

def check_flow_balance_testnet(address):
    """
    Verifica o saldo de uma conta Flow APENAS NA TESTNET
    """
    # Remove 0x prefix se existir
    if address.startswith('0x'):
        address = address[2:]

    # URL da API Flow TESTNET apenas
    testnet_url = f"https://rest-testnet.onflow.org/v1/accounts/{address}"

    print(f"🔍 Verificando saldo da conta Flow (TESTNET): 0x{address}\n")

    # Consultar apenas testnet
    try:
        print("📊 Consultando Testnet...")
        response = requests.get(testnet_url, timeout=5)  # Timeout menor para ser mais rápido
        if response.status_code == 200:
            data = response.json()
            balance = float(data.get('balance', 0)) / 100000000  # Converter de menor unidade para FLOW
            print(f"✅ Testnet:")
            print(f"   Saldo: {balance:.8f} FLOW")
            print(f"   Endereço: 0x{address}")

            # Mostrar informação adicional se disponível
            if 'keys' in data:
                print(f"   Chaves: {len(data['keys'])} chave(s) configurada(s)")
            if 'contracts' in data:
                contracts = data.get('contracts', {})
                if contracts:
                    print(f"   Contratos: {', '.join(contracts.keys())}")

            return data
        elif response.status_code == 404:
            print("❌ Conta não encontrada na Testnet")
            print("💡 Dica: Certifique-se de que o endereço está correto")
            print("🔗 Criar conta: https://testnet-faucet.onflow.org/")
        else:
            print(f"⚠️ Status HTTP: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⏱️ Timeout ao acessar Testnet (5 segundos)")
    except Exception as e:
        print(f"⚠️ Erro ao acessar Testnet: {e}")

    return None

if __name__ == "__main__":
    # Endereço padrão do projeto
    address = "0x25f823e2a115b2dc"

    if len(sys.argv) > 1:
        address = sys.argv[1]

    check_flow_balance_testnet(address)