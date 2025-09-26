#!/usr/bin/env python3

import requests
import json
import time
from pathlib import Path

# Configuração
FLOW_API = "https://rest-testnet.onflow.org/v1"
CONTRACT_ADDRESS = "0x36395f9dde50ea27"
ACCOUNT_ADDRESS = "0x36395f9dde50ea27"

def check_contract_status():
    """Verifica se o contrato está deployado"""
    url = f"{FLOW_API}/accounts/{CONTRACT_ADDRESS}"
    response = requests.get(url)

    if response.status_code == 200:
        account_data = response.json()
        contracts = account_data.get('contracts', {})

        if 'HackathonBadge' in contracts:
            print("✅ Contrato HackathonBadge encontrado!")
            return True
        else:
            print("❌ Contrato HackathonBadge não encontrado")
            # Listar contratos existentes
            if contracts:
                print("📦 Contratos deployados nesta conta:")
                for name in contracts.keys():
                    print(f"   - {name}")
            return False
    else:
        print(f"❌ Erro ao verificar conta: {response.status_code}")
        return False

def execute_script(script_code):
    """Executa um script Cadence"""
    url = f"{FLOW_API}/scripts"

    payload = {
        "script": script_code,
        "arguments": []
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao executar script: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🚀 Verificação e Mint de HackathonBadge NFT")
    print("🌐 Rede: Flow Testnet")
    print(f"📍 Conta: {CONTRACT_ADDRESS}")
    print("=" * 60)

    # 1. Verificar status do contrato
    print("\n📊 1. Verificando contrato...")
    print("-" * 40)

    if not check_contract_status():
        print("\n💡 O contrato precisa ser deployado primeiro!")
        print("   Use: flow project deploy --update")
        return

    # 2. Verificar total supply atual
    print("\n📊 2. Verificando total de NFTs...")
    print("-" * 40)

    supply_script = f"""
    import HackathonBadge from {CONTRACT_ADDRESS}

    pub fun main(): UInt64 {{
        return HackathonBadge.totalSupply
    }}
    """

    result = execute_script(supply_script)
    if result:
        try:
            total = int(result.get('value', '0'))
            print(f"📈 Total de NFTs mintados: {total}")
        except:
            print("📈 Total: 0")

    # 3. Verificar um participante específico
    print("\n🔍 3. Verificando participante...")
    print("-" * 40)

    participant = "João Developer"
    event = "Flow Hackathon 2024"

    check_script = f'''
    import HackathonBadge from {CONTRACT_ADDRESS}

    pub fun main(): Bool {{
        return HackathonBadge.isRegistered(
            participantName: "{participant}",
            eventName: "{event}"
        )
    }}
    '''

    result = execute_script(check_script)
    if result:
        is_registered = result.get('value', 'false') == 'true'

        if is_registered:
            print(f"✅ Participante '{participant}' já está registrado!")

            # Buscar ID do badge
            id_script = f'''
            import HackathonBadge from {CONTRACT_ADDRESS}

            pub fun main(): UInt64? {{
                return HackathonBadge.getBadgeID(
                    participantName: "{participant}",
                    eventName: "{event}"
                )
            }}
            '''

            id_result = execute_script(id_script)
            if id_result and id_result.get('value'):
                badge_id = id_result['value']
                print(f"📦 Badge ID: {badge_id}")
                print(f"\n🔗 Ver NFT no Flowscan:")
                print(f"   https://testnet.flowscan.io/nft/A.{CONTRACT_ADDRESS[2:]}.HackathonBadge.NFT/{badge_id}")
        else:
            print(f"❌ Participante '{participant}' não está registrado")

    # 4. Informações para mintar
    print("\n💡 4. Como mintar um novo NFT...")
    print("-" * 40)
    print("Execute a seguinte transação com flow CLI:")
    print()
    print("flow transactions send transactions/mint_hackathon_badge.cdc \\")
    print('  "Seu Nome" "Flow Hackathon 2024" 10.0 \\')
    print("  --network testnet --signer bootcamp-account")

    # 5. Links úteis
    print("\n🔗 5. Links Úteis")
    print("-" * 40)
    print(f"📊 Ver conta: https://testnet.flowscan.io/account/{CONTRACT_ADDRESS}")
    print(f"📦 Ver coleção: https://testnet.flowscan.io/nft/A.{CONTRACT_ADDRESS[2:]}.HackathonBadge.NFT")
    print(f"💧 Faucet: https://testnet-faucet.onflow.org/")

    print("\n" + "=" * 60)
    print("🏁 Verificação concluída!")

if __name__ == "__main__":
    main()