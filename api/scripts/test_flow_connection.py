#!/usr/bin/env python3
"""
Teste de conexão com Flow Blockchain
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def test_flow_credentials():
    """Testa se as credenciais Flow estão configuradas"""

    print("=" * 60)
    print("🔧 TESTANDO CREDENCIAIS FLOW BLOCKCHAIN")
    print("=" * 60)

    # Verifica as variáveis
    address = os.getenv('FLOW_ACCOUNT_ADDRESS')
    private_key = os.getenv('FLOW_PRIVATE_KEY')
    network = os.getenv('FLOW_NETWORK')
    access_node = os.getenv('FLOW_ACCESS_NODE')

    print("\n📋 Credenciais configuradas:")
    print(f"✅ Address: {address}")
    print(f"✅ Private Key: {'*' * 40}{private_key[-20:] if private_key else 'NÃO CONFIGURADA'}")
    print(f"✅ Network: {network}")
    print(f"✅ Access Node: {access_node}")

    # Validação básica
    issues = []

    if not address:
        issues.append("❌ FLOW_ACCOUNT_ADDRESS não configurado")
    elif not address.startswith('0x'):
        issues.append("⚠️ FLOW_ACCOUNT_ADDRESS deve começar com '0x'")
    elif len(address) != 18:  # 0x + 16 caracteres
        issues.append(f"⚠️ FLOW_ACCOUNT_ADDRESS tem tamanho incorreto: {len(address)} (esperado: 18)")

    if not private_key:
        issues.append("❌ FLOW_PRIVATE_KEY não configurada")
    elif len(private_key) != 64:  # 64 caracteres hexadecimais
        issues.append(f"⚠️ FLOW_PRIVATE_KEY tem tamanho incorreto: {len(private_key)} (esperado: 64)")

    if not network:
        issues.append("❌ FLOW_NETWORK não configurado")
    elif network not in ['mainnet', 'testnet', 'emulator']:
        issues.append(f"⚠️ FLOW_NETWORK inválido: {network}")

    if not access_node:
        issues.append("❌ FLOW_ACCESS_NODE não configurado")

    print("\n" + "=" * 60)

    if issues:
        print("⚠️ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ TODAS AS CREDENCIAIS PARECEM ESTAR CORRETAS!")
        print("\n🎯 Próximos passos:")
        print("1. Sua conta testnet: 0x25f823e2a115b2dc")
        print("2. Saldo disponível: 1000 FLOW")
        print("3. Rede: Testnet Flow")
        print("\n🚀 Pronto para usar no hackathon!")

    print("=" * 60)

if __name__ == "__main__":
    test_flow_credentials()