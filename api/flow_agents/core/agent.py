"""
Flow Agent - Classe principal do agente autônomo
"""

import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import os
from ..services.neo4j_service import Neo4jMemory
from ..actions.transactions import TransactionBuilder
from ..actions.scripts import ScriptExecutor

class FlowAgent:
    """
    Agente autônomo para Flow Blockchain
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Inicializa o Flow Agent

        Args:
            name: Nome do agente
            config: Configurações do agente
        """
        self.name = name
        self.config = config
        self.account_address = config.get("account_address", "")
        self.private_key = config.get("private_key", "")
        self.network = config.get("network", "testnet")

        # Serviços
        self.memory = None
        self.transaction_builder = TransactionBuilder(self)
        self.script_executor = ScriptExecutor(self)

        # Estado
        self.is_running = False
        self.stats = {
            "transactions_sent": 0,
            "scripts_executed": 0,
            "events_processed": 0,
            "start_time": None
        }

        # Actions registradas
        self.actions = {}

        # Scheduled tasks
        self.scheduled_tasks = []

    async def initialize(self):
        """
        Inicializa o agente e seus serviços
        """
        print(f"🚀 Inicializando Flow Agent: {self.name}")

        # Conectar Neo4j se configurado
        if self.config.get("neo4j"):
            self.memory = Neo4jMemory(self.config["neo4j"])
            await self.memory.connect()
            print("✅ Neo4j conectado")

        # Verificar conta Flow
        account_info = await self.get_account_info()
        if account_info:
            print(f"✅ Conta Flow: {self.account_address}")
            print(f"   Saldo: {account_info.get('balance', 0)} FLOW")

        self.is_running = True
        self.stats["start_time"] = datetime.now()

        print(f"✅ Agent {self.name} inicializado com sucesso!")

    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtém informações da conta Flow
        """
        try:
            cmd = [
                "flow", "accounts", "get", self.account_address,
                "--network", self.network,
                "--output", "json"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "address": self.account_address,
                    "balance": float(data.get("balance", 0)) / 100000000,
                    "keys": data.get("keys", []),
                    "contracts": list(data.get("contracts", {}).keys())
                }
        except Exception as e:
            print(f"❌ Erro ao obter info da conta: {e}")

        return None

    def register_action(self, name: str, handler: Callable):
        """
        Registra uma action customizada

        Args:
            name: Nome da action
            handler: Função handler
        """
        self.actions[name] = handler
        print(f"✅ Action registrada: {name}")

    async def execute_action(self, action_name: str, params: Dict[str, Any] = None):
        """
        Executa uma action registrada

        Args:
            action_name: Nome da action
            params: Parâmetros da action

        Returns:
            Resultado da action
        """
        if action_name not in self.actions:
            raise ValueError(f"Action não encontrada: {action_name}")

        handler = self.actions[action_name]

        # Log no Neo4j se disponível
        if self.memory:
            await self.memory.create_memory({
                "type": "action_execution",
                "action": action_name,
                "params": params,
                "timestamp": datetime.now().isoformat()
            })

        # Executar handler
        result = await handler(params or {})

        return result

    async def transfer_flow(self, to: str, amount: float) -> Dict[str, Any]:
        """
        Transfere FLOW tokens

        Args:
            to: Endereço de destino
            amount: Quantidade de FLOW

        Returns:
            Resultado da transação
        """
        cadence = '''
        import FlowToken from 0x1654653399040a61
        import FungibleToken from 0xf233dcee88fe0abe

        transaction(amount: UFix64, to: Address) {
            let sentVault: @FungibleToken.Vault

            prepare(signer: AuthAccount) {
                let vaultRef = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
                    ?? panic("Could not borrow reference to the owner's Vault!")

                self.sentVault <- vaultRef.withdraw(amount: amount)
            }

            execute {
                let recipient = getAccount(to)
                let receiverRef = recipient.getCapability(/public/flowTokenReceiver)
                    .borrow<&{FungibleToken.Receiver}>()
                    ?? panic("Could not borrow receiver reference")

                receiverRef.deposit(from: <-self.sentVault)
            }
        }
        '''

        result = await self.transaction_builder.send(
            cadence=cadence,
            args=[
                {"type": "UFix64", "value": str(amount)},
                {"type": "Address", "value": to}
            ]
        )

        self.stats["transactions_sent"] += 1

        # Log no Neo4j
        if self.memory:
            await self.memory.create_memory({
                "type": "transfer",
                "from": self.account_address,
                "to": to,
                "amount": amount,
                "tx_id": result.get("transaction_id"),
                "timestamp": datetime.now().isoformat()
            })

        return result

    async def execute_script(self, cadence: str, args: List[Any] = None) -> Any:
        """
        Executa um script Cadence

        Args:
            cadence: Código Cadence
            args: Argumentos do script

        Returns:
            Resultado do script
        """
        result = await self.script_executor.execute(cadence, args or [])
        self.stats["scripts_executed"] += 1
        return result

    def schedule_task(self, name: str, interval: int, task: Callable):
        """
        Agenda uma tarefa recorrente

        Args:
            name: Nome da tarefa
            interval: Intervalo em segundos
            task: Função a executar
        """
        self.scheduled_tasks.append({
            "name": name,
            "interval": interval,
            "task": task,
            "last_run": None
        })
        print(f"⏰ Tarefa agendada: {name} (a cada {interval}s)")

    async def run_scheduled_tasks(self):
        """
        Executa tarefas agendadas
        """
        while self.is_running:
            for task_info in self.scheduled_tasks:
                now = datetime.now()

                if task_info["last_run"] is None or \
                   (now - task_info["last_run"]).total_seconds() >= task_info["interval"]:

                    try:
                        await task_info["task"]()
                        task_info["last_run"] = now
                    except Exception as e:
                        print(f"❌ Erro na tarefa {task_info['name']}: {e}")

            await asyncio.sleep(1)

    async def monitor_events(self, event_type: str, callback: Callable):
        """
        Monitora eventos na blockchain

        Args:
            event_type: Tipo de evento
            callback: Função callback
        """
        print(f"👁️ Monitorando eventos: {event_type}")

        # Implementação simplificada - em produção usar Flow SDK
        while self.is_running:
            try:
                # Simular recepção de evento
                await asyncio.sleep(10)

                event = {
                    "type": event_type,
                    "data": {},
                    "block_height": 12345,
                    "timestamp": datetime.now().isoformat()
                }

                await callback(event)
                self.stats["events_processed"] += 1

            except Exception as e:
                print(f"❌ Erro monitorando eventos: {e}")

    async def run(self):
        """
        Loop principal do agente
        """
        if not self.is_running:
            await self.initialize()

        print(f"🤖 Agent {self.name} está rodando...")

        # Iniciar tarefas agendadas
        tasks = [self.run_scheduled_tasks()]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"⏹️ Parando agent {self.name}...")
            await self.shutdown()

    async def shutdown(self):
        """
        Desliga o agente graciosamente
        """
        self.is_running = False

        # Desconectar Neo4j
        if self.memory:
            await self.memory.disconnect()

        # Mostrar estatísticas finais
        print(f"\n📊 Estatísticas do Agent {self.name}:")
        print(f"   Transações enviadas: {self.stats['transactions_sent']}")
        print(f"   Scripts executados: {self.stats['scripts_executed']}")
        print(f"   Eventos processados: {self.stats['events_processed']}")

        if self.stats["start_time"]:
            uptime = datetime.now() - self.stats["start_time"]
            print(f"   Uptime: {uptime}")

        print(f"✅ Agent {self.name} desligado com sucesso!")

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do agente
        """
        stats = self.stats.copy()
        if stats["start_time"]:
            stats["uptime"] = str(datetime.now() - stats["start_time"])
        return stats