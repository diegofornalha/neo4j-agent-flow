#!/usr/bin/env python3
"""
🤖 Hello Flow Agent - Primeiro Agente Inteligente na Flow Blockchain
Este agente demonstra a integração básica entre Claude Code SDK e Flow Blockchain
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Flow SDK (Modo demonstração - sem dependências reais)
# Em produção, use: from flow_py_sdk import flow_client, Script
# from flow_py_sdk.cadence import Address, UInt64

# Mock para demonstração
class flow_client:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port

# Claude Code SDK (simulado para exemplo)
# Em produção, use: from claude_code_sdk import query, ClaudeCodeOptions

@dataclass
class FlowAgentConfig:
    """Configuração do agente Flow"""
    name: str = "HelloFlowAgent"
    flow_network: str = "emulator"  # emulator, testnet, mainnet
    flow_access_node: str = "http://localhost:8888"
    decision_model: str = "claude-3-5-sonnet"
    monitoring_interval: int = 10  # segundos

class FlowBlockchainAgent:
    """
    Agente inteligente que monitora e interage com a Flow Blockchain
    """

    def __init__(self, config: FlowAgentConfig):
        self.config = config
        self.client = None
        self.is_running = False
        self.knowledge_base = {}
        self.transaction_history = []

    async def initialize(self):
        """Inicializa conexão com Flow"""
        print(f"🚀 Iniciando {self.config.name}...")

        # Conecta com Flow
        self.client = flow_client(
            host=self.config.flow_access_node.split("://")[1].split(":")[0],
            port=int(self.config.flow_access_node.split(":")[-1])
        )

        # Testa conexão
        latest_block = await self.get_latest_block()
        print(f"✅ Conectado à Flow! Bloco atual: {latest_block['height']}")

    async def get_latest_block(self) -> Dict[str, Any]:
        """Obtém o bloco mais recente"""
        # Em produção, use flow_py_sdk
        # Por enquanto, retorna mock
        return {
            "height": 12345678,
            "id": "0xabc123...",
            "timestamp": datetime.now().isoformat(),
            "transactions": []
        }

    async def monitor_events(self):
        """Monitora eventos na blockchain"""
        print("👁️ Monitorando eventos na Flow...")

        while self.is_running:
            try:
                # Obtém último bloco
                block = await self.get_latest_block()

                # Analisa com AI
                analysis = await self.analyze_with_ai(block)

                # Toma decisão
                if analysis.get("action_required"):
                    await self.execute_action(analysis["action"])

                # Aguarda próximo ciclo
                await asyncio.sleep(self.config.monitoring_interval)

            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                await asyncio.sleep(5)

    async def analyze_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa Claude Code SDK para analisar dados da blockchain
        """
        # Em produção:
        # prompt = f"Analise este bloco da Flow: {json.dumps(data)}"
        # response = await query(prompt, ClaudeCodeOptions(
        #     model=self.config.decision_model,
        #     temperature=0.3
        # ))

        # Mock para exemplo
        return {
            "block_height": data["height"],
            "analysis": "Bloco normal, sem anomalias detectadas",
            "action_required": False,
            "confidence": 0.95
        }

    async def execute_action(self, action: Dict[str, Any]):
        """
        Executa ação na blockchain baseada na decisão da AI
        """
        print(f"⚡ Executando ação: {action.get('type', 'unknown')}")

        # Exemplos de ações:
        # - Enviar transação
        # - Interagir com smart contract
        # - Alertar usuário
        # - Atualizar conhecimento

        self.transaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": "completed"
        })

    async def query_smart_contract(self, contract_address: str, script: str) -> Any:
        """
        Consulta um smart contract na Flow
        """
        # Em produção, use flow_py_sdk.Script
        result = {
            "contract": contract_address,
            "data": "mock_data"
        }

        # Armazena no conhecimento
        self.knowledge_base[contract_address] = result

        return result

    async def send_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Envia transação para a Flow
        """
        print(f"📤 Enviando transação: {transaction.get('type')}")

        # Em produção, construa e envie transação real
        tx_id = f"0x{datetime.now().timestamp()}"

        return tx_id

    async def learn_from_experience(self):
        """
        Agente aprende com suas experiências
        """
        if len(self.transaction_history) > 10:
            # Analisa histórico
            successful = [tx for tx in self.transaction_history if tx["status"] == "completed"]
            success_rate = len(successful) / len(self.transaction_history)

            print(f"📊 Taxa de sucesso: {success_rate:.1%}")

            # Ajusta estratégia baseado no aprendizado
            if success_rate < 0.8:
                print("🔧 Ajustando estratégia do agente...")
                self.config.monitoring_interval += 5

    async def start(self):
        """Inicia o agente"""
        self.is_running = True
        await self.initialize()

        # Tarefas paralelas
        tasks = [
            asyncio.create_task(self.monitor_events()),
            asyncio.create_task(self.periodic_learning())
        ]

        await asyncio.gather(*tasks)

    async def periodic_learning(self):
        """Aprendizado periódico"""
        while self.is_running:
            await asyncio.sleep(60)  # Aprende a cada minuto
            await self.learn_from_experience()

    def stop(self):
        """Para o agente"""
        self.is_running = False
        print(f"🛑 {self.config.name} parado")

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do agente"""
        return {
            "name": self.config.name,
            "network": self.config.flow_network,
            "is_running": self.is_running,
            "transactions": len(self.transaction_history),
            "knowledge_items": len(self.knowledge_base)
        }


# Exemplo de Smart Contract Cadence que o agente pode interagir
HELLO_WORLD_CONTRACT = """
pub contract HelloWorld {

    pub var greeting: String
    pub var interactionCount: UInt64

    pub event AgentInteraction(agent: Address, message: String)

    init() {
        self.greeting = "Hello from Flow!"
        self.interactionCount = 0
    }

    pub fun updateGreeting(newGreeting: String) {
        self.greeting = newGreeting
        self.interactionCount = self.interactionCount + 1
    }

    pub fun getGreeting(): String {
        return self.greeting
    }

    pub fun getStats(): {String: UInt64} {
        return {
            "interactions": self.interactionCount
        }
    }
}
"""


async def main():
    """Função principal de demonstração"""

    print("=" * 50)
    print("🤖 Flow Blockchain Agent - Demo")
    print("=" * 50)

    # Configura agente
    config = FlowAgentConfig(
        name="DemoFlowAgent",
        flow_network="emulator",
        monitoring_interval=5
    )

    # Cria e inicia agente
    agent = FlowBlockchainAgent(config)

    try:
        # Inicializa
        await agent.initialize()

        # Demonstra capacidades
        print("\n📋 Capacidades do Agente:")
        print("1. Monitora blockchain em tempo real")
        print("2. Analisa dados com AI (Claude)")
        print("3. Executa transações automaticamente")
        print("4. Aprende com experiências")
        print("5. Interage com smart contracts")

        # Simula algumas operações
        print("\n🔄 Executando operações de demonstração...")

        # 1. Consulta contrato
        result = await agent.query_smart_contract(
            "0x01",
            "HelloWorld.getGreeting()"
        )
        print(f"✅ Consultou contrato: {result}")

        # 2. Analisa bloco
        block = await agent.get_latest_block()
        analysis = await agent.analyze_with_ai(block)
        print(f"🧠 Análise AI: {analysis['analysis']}")

        # 3. Envia transação (mock)
        tx_id = await agent.send_transaction({
            "type": "greeting_update",
            "data": {"message": "Hello from Agent!"}
        })
        print(f"📤 Transação enviada: {tx_id}")

        # Status final
        print(f"\n📊 Status do Agente:")
        status = agent.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")

    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    finally:
        agent.stop()

    print("\n✅ Demo concluída!")


if __name__ == "__main__":
    # Roda o agente
    asyncio.run(main())