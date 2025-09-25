"""
Flow Name Service - Sistema Completo de Registro e Transferência
Para uso no hackathon - Registro de nomes para participantes
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import re

# Importar integração Neo4j
try:
    from .neo4j_integration import FNSNeo4jIntegration
except ImportError:
    FNSNeo4jIntegration = None

@dataclass
class RegistrationRequest:
    """Requisição de registro de nome .find"""
    buyer_address: str  # Quem está comprando (pagador)
    recipient_address: str  # Quem vai receber o nome
    name: str  # Nome desejado (sem .find)
    tier: str  # exclusive, premium, standard
    fee: float  # Taxa em FLOW
    quiz_badge: Optional[str] = None  # Badge do quiz se houver
    discount: float = 0.0  # Desconto aplicado

class FindRegistrationService:
    """
    Serviço completo para registro e transferência de nomes .find
    Permite que alguém compre um nome e transfira para outro endereço
    """

    def __init__(self, network: str = "testnet"):
        self.network = network
        self.testnet_contract = "0x35717efbbce11c74"
        self.mainnet_contract = "0x097bafa4e0b48eef"
        self.contract = self.testnet_contract if network == "testnet" else self.mainnet_contract

        # Cache de registros processados
        self.pending_registrations = {}
        self.completed_registrations = []

        # Inicializar integração Neo4j se disponível
        self.neo4j = None
        if FNSNeo4jIntegration:
            try:
                self.neo4j = FNSNeo4jIntegration()
                print("✅ Neo4j integração inicializada para Registration Service")
            except Exception as e:
                print(f"⚠️ Neo4j não disponível: {e}")

    # ========== REGISTRO DE NOMES ==========

    async def register_for_participant(
        self,
        buyer_address: str,
        participant_name: str,
        participant_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra um nome .find para um participante do evento

        Args:
            buyer_address: Endereço que vai pagar (organizador)
            participant_name: Nome do participante (será o nome .find)
            participant_address: Endereço do participante (opcional)

        Returns:
            Status do registro
        """
        # Limpar e validar nome
        clean_name = self._clean_name(participant_name)
        validation = self._validate_name_format(clean_name)

        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }

        # Determinar tier e preço
        tier = self._get_name_tier(clean_name)
        base_fee = self._calculate_fee(clean_name)

        # Criar requisição
        request = RegistrationRequest(
            buyer_address=buyer_address,
            recipient_address=participant_address or buyer_address,
            name=clean_name,
            tier=tier,
            fee=base_fee
        )

        # Adicionar à fila
        request_id = f"reg_{clean_name}_{datetime.now().timestamp()}"
        self.pending_registrations[request_id] = request

        # Salvar no Neo4j se disponível
        if self.neo4j:
            try:
                self.neo4j.save_name_registration(
                    name=clean_name,
                    owner_address=request.recipient_address,
                    buyer_address=request.buyer_address,
                    tier=tier,
                    fee=base_fee,
                    transaction_id=request_id
                )
            except Exception as e:
                print(f"Erro ao salvar registro no Neo4j: {e}")

        return {
            "success": True,
            "request_id": request_id,
            "name": f"{clean_name}.find",
            "recipient": request.recipient_address,
            "fee": base_fee,
            "tier": tier,
            "status": "pending_payment",
            "message": f"Registro preparado. Custo: {base_fee} FLOW"
        }

    async def batch_register_participants(
        self,
        buyer_address: str,
        participants: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Registra múltiplos nomes de uma vez

        Args:
            buyer_address: Quem paga por todos
            participants: Lista de {"name": "joão", "address": "0x..."}

        Returns:
            Status de todos os registros
        """
        results = []
        total_cost = 0.0

        for participant in participants:
            name = participant.get("name")
            address = participant.get("address", buyer_address)

            result = await self.register_for_participant(
                buyer_address=buyer_address,
                participant_name=name,
                participant_address=address
            )

            if result["success"]:
                total_cost += result["fee"]

            results.append(result)

        return {
            "success": True,
            "total_participants": len(participants),
            "successful_preparations": sum(1 for r in results if r["success"]),
            "total_cost": total_cost,
            "registrations": results,
            "message": f"Preparados {len(results)} registros. Custo total: {total_cost} FLOW"
        }

    # ========== TRANSFERÊNCIA DE NFTs ==========

    async def transfer_name_nft(
        self,
        from_address: str,
        to_address: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Transfere a propriedade de um nome .find (NFT) para outro endereço

        Args:
            from_address: Proprietário atual
            to_address: Novo proprietário
            name: Nome .find a transferir

        Returns:
            Status da transferência
        """
        clean_name = self._clean_name(name)

        # Verificar propriedade atual
        current_owner = await self._get_name_owner(clean_name)

        if current_owner != from_address:
            return {
                "success": False,
                "error": f"Endereço {from_address} não é o dono de {clean_name}.find"
            }

        # Preparar transação de transferência
        # Nota: Isso seria uma transação Cadence real em produção
        transaction_data = {
            "type": "transfer_nft",
            "from": from_address,
            "to": to_address,
            "nft_id": clean_name,
            "timestamp": datetime.now().isoformat()
        }

        # Salvar transferência no Neo4j
        if self.neo4j:
            try:
                self.neo4j.save_name_transfer(
                    name=clean_name,
                    from_address=from_address,
                    to_address=to_address,
                    transaction_id=f"transfer_{datetime.now().timestamp()}"
                )
            except Exception as e:
                print(f"Erro ao salvar transferência no Neo4j: {e}")

        return {
            "success": True,
            "transaction": transaction_data,
            "message": f"Nome {clean_name}.find transferido de {from_address[:8]}... para {to_address[:8]}..."
        }

    # ========== COMANDOS DO CHAT ==========

    def parse_registration_command(self, message: str, sender_address: str) -> Optional[Dict[str, Any]]:
        """
        Detecta e processa comandos de registro no chat

        Comandos suportados:
        - "registrar joão para 0x123..."
        - "comprar maria.find"
        - "registro em lote: joão, maria, pedro"
        - "transferir alice.find para 0x456..."
        """
        message_lower = message.lower().strip()

        # Registro simples
        match = re.match(r"registrar\s+(\w+)(?:\s+para\s+(0x[a-f0-9]+))?", message_lower)
        if match:
            name = match.group(1)
            recipient = match.group(2) or sender_address
            return {
                "action": "register",
                "name": name,
                "recipient": recipient,
                "sender": sender_address
            }

        # Compra direta
        match = re.match(r"comprar\s+(\w+)\.?find", message_lower)
        if match:
            return {
                "action": "buy",
                "name": match.group(1),
                "buyer": sender_address
            }

        # Registro em lote
        match = re.match(r"registro\s+em\s+lote:\s*(.+)", message_lower)
        if match:
            names = [n.strip() for n in match.group(1).split(",")]
            return {
                "action": "batch_register",
                "names": names,
                "buyer": sender_address
            }

        # Transferência
        match = re.match(r"transferir\s+(\w+)\.?find\s+para\s+(0x[a-f0-9]+)", message_lower)
        if match:
            return {
                "action": "transfer",
                "name": match.group(1),
                "from": sender_address,
                "to": match.group(2)
            }

        return None

    async def process_chat_command(self, command: Dict[str, Any]) -> str:
        """
        Processa comando do chat e retorna resposta formatada
        """
        action = command.get("action")

        if action == "register":
            result = await self.register_for_participant(
                buyer_address=command["sender"],
                participant_name=command["name"],
                participant_address=command.get("recipient")
            )

            if result["success"]:
                return f"""✅ **Registro Preparado**

Nome: **{result['name']}**
Destinatário: `{result['recipient'][:8]}...`
Tier: {result['tier'].upper()}
Custo: **{result['fee']} FLOW**

Para confirmar, digite: `confirmar {result['request_id']}`"""
            else:
                return f"❌ Erro: {result['error']}"

        elif action == "buy":
            result = await self.register_for_participant(
                buyer_address=command["buyer"],
                participant_name=command["name"]
            )

            if result["success"]:
                return f"💰 Comprando **{result['name']}** por {result['fee']} FLOW"
            else:
                return f"❌ {result['error']}"

        elif action == "batch_register":
            participants = [{"name": n} for n in command["names"]]
            result = await self.batch_register_participants(
                buyer_address=command["buyer"],
                participants=participants
            )

            return f"""📋 **Registro em Lote**

Total: {result['total_participants']} nomes
Preparados: {result['successful_preparations']}
Custo Total: **{result['total_cost']} FLOW**

Nomes: {', '.join(r['name'] for r in result['registrations'] if r['success'])}"""

        elif action == "transfer":
            result = await self.transfer_name_nft(
                from_address=command["from"],
                to_address=command["to"],
                name=command["name"]
            )

            if result["success"]:
                return f"🔄 {result['message']}"
            else:
                return f"❌ {result['error']}"

        return "❓ Comando não reconhecido"

    # ========== GESTÃO DE EVENTO ==========

    async def create_event_registration_session(
        self,
        event_name: str,
        organizer_address: str,
        budget_flow: float
    ) -> Dict[str, Any]:
        """
        Cria sessão de registro para um evento

        Args:
            event_name: Nome do evento
            organizer_address: Endereço do organizador
            budget_flow: Orçamento em FLOW para registros

        Returns:
            Dados da sessão criada
        """
        session_id = f"event_{event_name}_{datetime.now().timestamp()}"

        session = {
            "id": session_id,
            "event": event_name,
            "organizer": organizer_address,
            "budget": budget_flow,
            "spent": 0.0,
            "registrations": [],
            "created_at": datetime.now().isoformat()
        }

        return {
            "success": True,
            "session": session,
            "message": f"Sessão criada para {event_name} com orçamento de {budget_flow} FLOW"
        }

    async def get_registration_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Retorna resumo de registros de uma sessão
        """
        # Em produção, isso consultaria o banco de dados
        registrations = [r for r in self.completed_registrations if r.get("session_id") == session_id]

        return {
            "session_id": session_id,
            "total_registrations": len(registrations),
            "total_cost": sum(r.get("fee", 0) for r in registrations),
            "names": [r.get("name") for r in registrations],
            "timestamp": datetime.now().isoformat()
        }

    # ========== HELPERS PRIVADOS ==========

    def _clean_name(self, name: str) -> str:
        """Limpa e normaliza nome"""
        return name.lower().replace('.find', '').replace('.fn', '').strip()

    def _validate_name_format(self, name: str) -> Dict[str, Any]:
        """Valida formato do nome"""
        if len(name) < 3:
            return {"valid": False, "error": "Nome muito curto (mínimo 3 caracteres)"}
        if len(name) > 16:
            return {"valid": False, "error": "Nome muito longo (máximo 16 caracteres)"}
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', name):
            return {"valid": False, "error": "Use apenas letras minúsculas, números e hífen"}
        return {"valid": True}

    def _get_name_tier(self, name: str) -> str:
        """Determina tier do nome"""
        length = len(name)
        if length <= 3:
            return "exclusive"
        elif length <= 5:
            return "premium"
        else:
            return "standard"

    def _calculate_fee(self, name: str) -> float:
        """Calcula taxa de registro"""
        tier = self._get_name_tier(name)
        fees = {
            "exclusive": 50.0,
            "premium": 15.0,
            "standard": 5.0
        }
        return fees[tier]

    async def _get_name_owner(self, name: str) -> Optional[str]:
        """Busca proprietário atual do nome"""
        # Em produção, consultaria a blockchain
        # Por enquanto, retorna None (disponível)
        return None

    def format_status_message(self, registrations: List[Dict]) -> str:
        """Formata mensagem de status para o chat"""
        if not registrations:
            return "📭 Nenhum registro pendente"

        msg = "📋 **Registros Pendentes**\n\n"
        total = 0.0

        for reg in registrations:
            msg += f"• **{reg['name']}** → `{reg['recipient'][:8]}...` ({reg['fee']} FLOW)\n"
            total += reg['fee']

        msg += f"\n💰 **Total: {total} FLOW**"
        return msg


# ========== Exemplo de Uso ==========

async def demo_registration_flow():
    """Demonstração do fluxo de registro"""
    service = FindRegistrationService(network="testnet")

    print("=" * 60)
    print("🎯 Flow Name Service - Registro para Eventos")
    print("=" * 60)

    # Criar sessão de evento
    event = await service.create_event_registration_session(
        event_name="Hackathon Flow AI",
        organizer_address="0x25f823e2a115b2dc",
        budget_flow=100.0
    )
    print(f"\n✅ {event['message']}")

    # Registrar participantes
    participants = [
        {"name": "alice", "address": "0x123..."},
        {"name": "bob", "address": "0x456..."},
        {"name": "carol", "address": "0x789..."}
    ]

    result = await service.batch_register_participants(
        buyer_address="0x25f823e2a115b2dc",
        participants=participants
    )

    print(f"\n📋 Registro em Lote:")
    print(f"   • Total: {result['total_participants']} participantes")
    print(f"   • Custo: {result['total_cost']} FLOW")

    # Simular comando do chat
    chat_commands = [
        "registrar diego para 0xabc123",
        "comprar hackathon.find",
        "registro em lote: team1, team2, team3",
        "transferir alice.find para 0xdef456"
    ]

    print("\n💬 Testando comandos do chat:")
    for cmd in chat_commands:
        print(f"\n→ Comando: '{cmd}'")
        parsed = service.parse_registration_command(cmd, "0x25f823e2a115b2dc")
        if parsed:
            response = await service.process_chat_command(parsed)
            print(f"← Resposta:\n{response}")

if __name__ == "__main__":
    asyncio.run(demo_registration_flow())