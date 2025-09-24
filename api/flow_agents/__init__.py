"""
Flow Agents - Plugin Python para Agentes Autônomos na Flow Blockchain
100% nativo, sem frameworks externos, puro Flow!
"""

from .core.agent import FlowAgent
from .core.client import FlowClient
from .actions.transactions import TransactionBuilder
from .actions.scripts import ScriptExecutor
from .services.neo4j_service import Neo4jMemory

__version__ = "1.0.0"
__all__ = [
    "FlowAgent",
    "FlowClient",
    "TransactionBuilder",
    "ScriptExecutor",
    "Neo4jMemory",
    "create_agent",
    "create_simple_agent"
]

def create_agent(name: str, config: dict = None) -> FlowAgent:
    """
    Factory function para criar um agente Flow

    Args:
        name: Nome do agente
        config: Configurações opcionais

    Returns:
        FlowAgent configurado
    """
    return FlowAgent(name=name, config=config or {})

def create_simple_agent(account_address: str, private_key: str) -> FlowAgent:
    """
    Cria um agente simples com configuração mínima

    Args:
        account_address: Endereço da conta Flow
        private_key: Chave privada

    Returns:
        FlowAgent pronto para uso
    """
    config = {
        "account_address": account_address,
        "private_key": private_key,
        "network": "testnet"
    }
    return FlowAgent(name="SimpleAgent", config=config)