"""
Exemplo de uso do Flow Agents Plugin
Demonstra como criar e usar um agente Flow Native em Python
"""

import asyncio
import os
from dotenv import load_dotenv
from flow_agents import create_agent

# Carregar variáveis de ambiente
load_dotenv()

async def main():
    """
    Exemplo principal de uso do Flow Agent
    """

    # Configuração do agente
    config = {
        "account_address": os.getenv("FLOW_ACCOUNT_ADDRESS"),
        "private_key": os.getenv("FLOW_PRIVATE_KEY"),
        "network": os.getenv("FLOW_NETWORK", "testnet"),
        "neo4j": {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "username": os.getenv("NEO4J_USERNAME", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "password")
        }
    }

    # Criar agente
    agent = create_agent("MeuAgenteFlow", config)

    # Inicializar
    await agent.initialize()

    # ========================================
    # EXEMPLOS DE OPERAÇÕES
    # ========================================

    print("\n🎯 DEMONSTRAÇÃO DO FLOW AGENT")
    print("=" * 50)

    # 1. Verificar informações da conta
    print("\n1️⃣ Informações da Conta:")
    account_info = await agent.get_account_info()
    if account_info:
        print(f"   Endereço: {account_info['address']}")
        print(f"   Saldo: {account_info['balance']} FLOW")
        print(f"   Contratos: {account_info['contracts']}")

    # 2. Executar um script simples
    print("\n2️⃣ Executar Script Cadence:")
    script = """
        pub fun main(): String {
            return "Hello from Flow!"
        }
    """
    result = await agent.execute_script(script)
    print(f"   Resultado: {result}")

    # 3. Registrar uma action customizada
    print("\n3️⃣ Registrar Action Customizada:")

    async def check_price_action(params):
        """Action para verificar preços"""
        token = params.get("token", "FLOW")
        # Aqui você faria a verificação real do preço
        return {
            "token": token,
            "price": 42.0,
            "timestamp": "2024-09-24T15:00:00Z"
        }

    agent.register_action("check_price", check_price_action)

    # 4. Executar action
    print("\n4️⃣ Executar Action:")
    price_result = await agent.execute_action("check_price", {"token": "FLOW"})
    print(f"   Preço do FLOW: ${price_result['price']}")

    # 5. Agendar tarefa recorrente
    print("\n5️⃣ Agendar Tarefa Recorrente:")

    async def monitor_balance():
        """Tarefa para monitorar saldo"""
        info = await agent.get_account_info()
        if info:
            print(f"   [Monitor] Saldo atual: {info['balance']} FLOW")

    agent.schedule_task("balance_monitor", interval=30, task=monitor_balance)

    # 6. Exemplo de transferência (comentado para segurança)
    print("\n6️⃣ Exemplo de Transferência (simulado):")
    print("   await agent.transfer_flow('0x123...', 1.0)")
    print("   # Transferiria 1 FLOW para 0x123...")

    # 7. Monitorar eventos (exemplo)
    print("\n7️⃣ Monitorar Eventos:")

    async def on_deposit_event(event):
        """Callback para eventos de depósito"""
        print(f"   💰 Depósito detectado: {event}")

    # Iniciar monitoramento em background
    asyncio.create_task(
        agent.monitor_events("A.0x1.FlowToken.TokensDeposited", on_deposit_event)
    )

    # ========================================
    # ESTATÍSTICAS
    # ========================================

    print("\n📊 Estatísticas do Agente:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 50)
    print("🎉 Demonstração concluída!")
    print("   Agent continua rodando em background...")
    print("   Pressione Ctrl+C para parar")

    # Manter agente rodando
    try:
        await agent.run()
    except KeyboardInterrupt:
        print("\n👋 Encerrando agent...")
        await agent.shutdown()

# ========================================
# EXEMPLOS ADICIONAIS
# ========================================

def exemplo_criar_agent_simples():
    """
    Exemplo de criação simplificada
    """
    from flow_agents import create_simple_agent

    agent = create_simple_agent(
        account_address="0x123...",
        private_key="abc123..."
    )
    return agent

def exemplo_actions_defi():
    """
    Exemplos de actions para DeFi
    """

    async def swap_tokens(params):
        """Swap de tokens em DEX"""
        token_in = params["token_in"]
        token_out = params["token_out"]
        amount = params["amount"]

        # Lógica do swap aqui
        return {
            "success": True,
            "amount_out": amount * 0.95,  # Simulando slippage
            "tx_id": "0xabc123..."
        }

    async def check_liquidity(params):
        """Verificar liquidez de pool"""
        pool = params["pool"]

        # Lógica de verificação aqui
        return {
            "pool": pool,
            "liquidity": 1000000,
            "apy": 12.5
        }

    return {
        "swap": swap_tokens,
        "liquidity": check_liquidity
    }

def exemplo_scheduled_tasks():
    """
    Exemplos de tarefas agendadas
    """

    async def auto_compound():
        """Auto-compound de rewards"""
        print("🔄 Executando auto-compound...")
        # Lógica aqui

    async def liquidation_check():
        """Verificar posições liquidáveis"""
        print("🔍 Verificando liquidações...")
        # Lógica aqui

    async def price_oracle_update():
        """Atualizar oracle de preços"""
        print("📊 Atualizando preços...")
        # Lógica aqui

    return {
        "auto_compound": (auto_compound, 3600),  # 1 hora
        "liquidation": (liquidation_check, 60),   # 1 minuto
        "oracle": (price_oracle_update, 300)       # 5 minutos
    }

# ========================================
# EXECUTAR EXEMPLO
# ========================================

if __name__ == "__main__":
    print("🌊 Flow Agents - Exemplo Python")
    print("=" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Exemplo finalizado!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")