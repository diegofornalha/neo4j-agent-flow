#!/usr/bin/env python3

import os
import json
from pathlib import Path
import subprocess
import time

# Configuração
CONTRACT_ADDRESS = "0x36395f9dde50ea27"
PRIVATE_KEY_PATH = "/Users/2a/Desktop/neo4j-agent-flow/api/TESTE.pkey"

def run_flow_command(command):
    """Executa comando flow com chave privada"""
    env = os.environ.copy()

    # Ler a chave privada
    with open(PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read().strip()

    env['FLOW_PRIVATE_KEY'] = private_key

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )

    return result

def main():
    print("🚀 Deploy e Mint de HackathonBadge NFT na Testnet")
    print("=" * 60)

    # 1. Deploy do contrato
    print("\n📦 1. Fazendo deploy do contrato HackathonBadge...")
    print("-" * 40)

    deploy_result = run_flow_command("flow project deploy --update")

    if deploy_result.returncode == 0:
        print("✅ Contrato deployado com sucesso!")
    else:
        print(f"❌ Erro no deploy: {deploy_result.stderr}")
        if "already exists" in deploy_result.stderr:
            print("ℹ️ Contrato já existe, continuando...")
        else:
            return

    # 2. Aguardar propagação
    print("\n⏰ Aguardando propagação na rede...")
    time.sleep(3)

    # 3. Mintar NFT
    print("\n🎯 2. Mintando HackathonBadge NFT...")
    print("-" * 40)

    # Parâmetros para o mint
    participant_name = "Developer João"
    event_name = "Flow Hackathon Testnet 2024"
    initial_prize = "5.0"

    print(f"📝 Participante: {participant_name}")
    print(f"🎪 Evento: {event_name}")
    print(f"💰 Prêmio inicial: {initial_prize} FLOW")

    # Executar transação de mint
    mint_command = f'''flow transactions send transactions/mint_hackathon_badge.cdc \
        "{participant_name}" "{event_name}" {initial_prize} \
        --network testnet \
        --signer bootcamp-account'''

    print(f"\n🔄 Executando transação...")
    mint_result = run_flow_command(mint_command)

    if mint_result.returncode == 0:
        print("✅ NFT mintado com sucesso!")

        # Extrair transaction ID da saída
        output_lines = mint_result.stdout.split('\n')
        for line in output_lines:
            if 'Transaction ID:' in line or 'ID:' in line:
                tx_id = line.split(':')[-1].strip()
                print(f"\n📋 Transaction ID: {tx_id}")
                print(f"🔗 Ver no Flowscan:")
                print(f"   https://testnet.flowscan.io/transaction/{tx_id}")
                break

        # Verificar o NFT mintado
        print("\n📊 3. Verificando NFT mintado...")
        print("-" * 40)

        # Script para verificar o badge
        check_script = f'''
import HackathonBadge from {CONTRACT_ADDRESS}

pub fun main(): UInt64? {{
    return HackathonBadge.getBadgeID(
        participantName: "{participant_name}",
        eventName: "{event_name}"
    )
}}
'''

        # Salvar script temporário
        script_path = Path("scripts/check_badge.cdc")
        script_path.write_text(check_script)

        # Executar script
        check_command = "flow scripts execute scripts/check_badge.cdc --network testnet"
        check_result = run_flow_command(check_command)

        if check_result.returncode == 0:
            # Tentar extrair o ID do badge
            try:
                # Procurar por número na saída
                import re
                match = re.search(r'Result:\s*(\d+)', check_result.stdout)
                if match:
                    badge_id = match.group(1)
                    print(f"✅ Badge ID: {badge_id}")
                    print(f"\n🎉 NFT criado com sucesso!")
                    print(f"🔗 Ver NFT no Flowscan:")
                    print(f"   https://testnet.flowscan.io/nft/A.{CONTRACT_ADDRESS[2:]}.HackathonBadge.NFT/{badge_id}")
                else:
                    print("✅ Badge criado (ID será visível em breve)")
            except:
                print("✅ Badge criado com sucesso!")

    else:
        print(f"❌ Erro ao mintar NFT: {mint_result.stderr}")
        print(f"Output: {mint_result.stdout}")

    # 4. Verificar total supply
    print("\n📈 4. Estatísticas da coleção...")
    print("-" * 40)

    supply_script = f'''
import HackathonBadge from {CONTRACT_ADDRESS}

pub fun main(): UInt64 {{
    return HackathonBadge.totalSupply
}}
'''

    script_path = Path("scripts/check_supply.cdc")
    script_path.write_text(supply_script)

    supply_command = "flow scripts execute scripts/check_supply.cdc --network testnet"
    supply_result = run_flow_command(supply_command)

    if supply_result.returncode == 0:
        try:
            import re
            match = re.search(r'Result:\s*(\d+)', supply_result.stdout)
            if match:
                total_supply = match.group(1)
                print(f"📊 Total de NFTs mintados: {total_supply}")
        except:
            pass

    print("\n" + "=" * 60)
    print("🏁 Processo concluído!")
    print(f"🌐 Contrato: https://testnet.flowscan.io/account/{CONTRACT_ADDRESS}")

if __name__ == "__main__":
    main()