#!/usr/bin/env python3
"""
Script para verificar saldo de conta Flow
"""

import requests
import json
import sys

def check_flow_balance(address):
    """
    Verifica o saldo de uma conta Flow usando a API pública
    """
    # Remove 0x prefix se existir
    if address.startswith('0x'):
        address = address[2:]

    # URLs da API Flow
    mainnet_url = f"https://rest-mainnet.onflow.org/v1/accounts/{address}"
    testnet_url = f"https://rest-testnet.onflow.org/v1/accounts/{address}"

    print(f"🔍 Verificando saldo da conta Flow: 0x{address}\n")

    # Tentar mainnet primeiro
    try:
        print("📊 Consultando Mainnet...")
        response = requests.get(mainnet_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            balance = float(data.get('balance', 0)) / 100000000  # Converter de menor unidade para FLOW
            print(f"✅ Mainnet:")
            print(f"   Saldo: {balance:.8f} FLOW")
            print(f"   Endereço: 0x{address}")
            return
        elif response.status_code == 404:
            print("❌ Conta não encontrada na Mainnet")
    except Exception as e:
        print(f"⚠️ Erro ao acessar Mainnet: {e}")

    # Tentar testnet
    try:
        print("\n📊 Consultando Testnet...")
        response = requests.get(testnet_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            balance = float(data.get('balance', 0)) / 100000000  # Converter de menor unidade para FLOW
            print(f"✅ Testnet:")
            print(f"   Saldo: {balance:.8f} FLOW")
            print(f"   Endereço: 0x{address}")
            return
        elif response.status_code == 404:
            print("❌ Conta não encontrada na Testnet")
    except Exception as e:
        print(f"⚠️ Erro ao acessar Testnet: {e}")

    print("\n❌ Não foi possível encontrar a conta em nenhuma rede Flow")

if __name__ == "__main__":
    # Endereço fornecido
    address = "0x25f823e2a115b2dc"

    if len(sys.argv) > 1:
        address = sys.argv[1]

    check_flow_balance(address)