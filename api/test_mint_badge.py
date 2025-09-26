#!/usr/bin/env python3

import asyncio
from flow_py_sdk import flow_client, ProposalKey, Tx, TransactionStatus
from flow_py_sdk.cadence import Address, String, UFix64
from flow_py_sdk.signer import in_memory_signer
from pathlib import Path

# Configuração - Testnet
FLOW_ACCESS_NODE = "https://rest-testnet.onflow.org"
CONTRACT_ADDRESS = "0x36395f9dde50ea27"

async def mint_badge():
    print("🎯 Mintando HackathonBadge NFT...")
    print("=" * 50)

    async with flow_client(
        host=FLOW_ACCESS_NODE,
        port=443
    ) as client:

        # Ler a transação
        tx_path = Path("transactions/mint_hackathon_badge.cdc")
        tx_code = tx_path.read_text()

        # Configurar conta de teste (conta pública sem chave privada)
        # Vamos apenas visualizar o script, não executar
        print("📝 Transação para mintar badge:")
        print("-" * 40)
        print(f"Participante: João Silva")
        print(f"Evento: Flow Hackathon 2024")
        print(f"Prêmio Inicial: 10.0 FLOW")
        print("-" * 40)

        # Criar script para verificar se já existe
        check_script = f"""
        import HackathonBadge from {CONTRACT_ADDRESS}

        access(all) fun main(): Bool {{
            return HackathonBadge.isRegistered(
                participantName: "João Silva",
                eventName: "Flow Hackathon 2024"
            )
        }}
        """

        try:
            # Verificar se já está registrado
            result = await client.execute_script(
                script=check_script
            )

            is_registered = result.as_type(bool)

            if is_registered:
                print("✅ Participante já está registrado!")

                # Buscar ID do badge
                get_id_script = f"""
                import HackathonBadge from {CONTRACT_ADDRESS}

                access(all) fun main(): UInt64? {{
                    return HackathonBadge.getBadgeID(
                        participantName: "João Silva",
                        eventName: "Flow Hackathon 2024"
                    )
                }}
                """

                id_result = await client.execute_script(
                    script=get_id_script
                )

                badge_id = id_result.value if id_result else None
                if badge_id:
                    print(f"📦 Badge ID: {badge_id}")
                    print(f"🔗 Ver no Flowscan:")
                    print(f"   https://testnet.flowscan.io/nft/A.{CONTRACT_ADDRESS[2:]}.HackathonBadge.NFT/{badge_id}")
            else:
                print("❌ Participante não está registrado ainda")
                print("\n💡 Para mintar, você precisaria:")
                print("1. Ter uma conta com chave privada")
                print("2. Ter FLOW tokens para o prêmio inicial")
                print("3. Executar a transação mint_hackathon_badge.cdc")

        except Exception as e:
            print(f"⚠️ Erro ao verificar: {e}")
            print("\n💭 O contrato pode não estar deployado ainda")

        # Verificar total supply
        supply_script = f"""
        import HackathonBadge from {CONTRACT_ADDRESS}

        access(all) fun main(): UInt64 {{
            return HackathonBadge.totalSupply
        }}
        """

        try:
            supply_result = await client.execute_script(
                script=supply_script
            )
            total = supply_result.value if supply_result else 0
            print(f"\n📊 Total de badges mintados: {total}")
        except:
            print("\n📊 Total de badges: não disponível")

if __name__ == "__main__":
    print("🚀 Testando HackathonBadge NFT")
    print("🌐 Rede: Flow Testnet")
    print(f"📍 Contrato: {CONTRACT_ADDRESS}")
    print("")
    asyncio.run(mint_badge())