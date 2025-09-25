"""
Flow Name Service (FNS) Integration for Neo4j Agent Flow
Complete implementation for .find name registration and management
"""

import asyncio
import aiohttp
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# Importar integração Neo4j
try:
    from .neo4j_integration import FNSNeo4jIntegration
except ImportError:
    FNSNeo4jIntegration = None

class NameTier(Enum):
    """Tiers de preço para nomes .find"""
    EXCLUSIVE = "exclusive"  # ≤3 caracteres - 50 FLOW
    PREMIUM = "premium"      # 4-5 caracteres - 15 FLOW
    STANDARD = "standard"    # ≥6 caracteres - 5 FLOW

@dataclass
class FNSConfig:
    """Configuração do FNS"""
    network: str = "testnet"
    testnet_contract: str = "0x35717efbbce11c74"
    mainnet_contract: str = "0x097bafa4e0b48eef"
    testnet_access_node: str = "access.devnet.nodes.onflow.org"
    testnet_port: str = "9000"
    faucet_url: str = "https://faucet.flow.com/fund-account"

class FindNameService:
    """
    Serviço completo para gerenciamento de nomes .find
    """

    def __init__(self, config: FNSConfig = None):
        self.config = config or FNSConfig()
        self.contract = self.config.testnet_contract if self.config.network == "testnet" else self.config.mainnet_contract
        self._cache = {}  # Cache simples para resoluções

        # Inicializar integração Neo4j se disponível
        self.neo4j = None
        if FNSNeo4jIntegration:
            try:
                self.neo4j = FNSNeo4jIntegration()
                print("✅ Neo4j integração inicializada para FNS")
            except Exception as e:
                print(f"⚠️ Neo4j não disponível: {e}")

    # ========== Validação e Verificação ==========

    def validate_name_format(self, name: str) -> Dict[str, Any]:
        """
        Valida formato do nome .find

        Regras:
        - 3-16 caracteres
        - Apenas alfanumérico e hífen
        - Lowercase
        - Não pode começar/terminar com hífen
        """
        # Remove .find se presente
        clean_name = name.replace('.find', '').replace('.fn', '')

        # Validações
        if len(clean_name) < 3:
            return {"valid": False, "error": "Nome muito curto (mínimo 3 caracteres)"}

        if len(clean_name) > 16:
            return {"valid": False, "error": "Nome muito longo (máximo 16 caracteres)"}

        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', clean_name):
            return {"valid": False, "error": "Formato inválido (use apenas letras minúsculas, números e hífen)"}

        return {"valid": True, "name": clean_name}

    def get_name_tier(self, name: str) -> NameTier:
        """Determina o tier de preço do nome"""
        clean_name = name.replace('.find', '')
        length = len(clean_name)

        if length <= 3:
            return NameTier.EXCLUSIVE
        elif length <= 5:
            return NameTier.PREMIUM
        else:
            return NameTier.STANDARD

    def calculate_registration_fee(self, name: str) -> float:
        """Calcula taxa de registro baseada no tier"""
        tier = self.get_name_tier(name)

        fees = {
            NameTier.EXCLUSIVE: 50.0,
            NameTier.PREMIUM: 15.0,
            NameTier.STANDARD: 5.0
        }

        return fees[tier]

    # ========== Resolução de Nomes ==========

    async def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve nome .find para endereço Flow

        Tenta múltiplas abordagens:
        1. Cache local
        2. API pública (se disponível)
        3. Contrato direto
        """
        clean_name = name.replace('.find', '').replace('.fn', '')

        # Verificar cache
        if clean_name in self._cache:
            return self._cache[clean_name]

        # Tentar API pública
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.find.xyz/resolve/{clean_name}"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        address = data.get("address")
                        if address:
                            self._cache[clean_name] = address
                            return address
        except:
            pass  # Fallback para contrato

        # TODO: Implementar chamada direta ao contrato via FCL
        return None

    async def reverse_lookup(self, address: str) -> Optional[str]:
        """Busca nome .find associado a um endereço"""
        # Normalizar endereço
        if not address.startswith('0x'):
            address = f'0x{address}'

        # Verificar cache reverso
        for name, cached_addr in self._cache.items():
            if cached_addr == address:
                return f"{name}.find"

        # TODO: Implementar busca reversa via contrato
        return None

    async def check_availability(self, name: str) -> bool:
        """Verifica se nome está disponível para registro"""
        validation = self.validate_name_format(name)
        if not validation["valid"]:
            return False

        resolved = await self.resolve_name(validation["name"])
        return resolved is None

    # ========== Perfil e Metadados ==========

    async def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém perfil completo de um nome .find"""
        clean_name = name.replace('.find', '')

        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.find.xyz/profile/{clean_name}"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        return await response.json()
        except:
            pass

        return None

    async def search_names(self, query: str, limit: int = 10) -> List[str]:
        """Busca nomes .find por query"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.find.xyz/search"
                params = {"q": query, "limit": limit}
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
        except:
            pass

        return []

    # ========== Quiz e Badges (Gamificação) ==========

    async def check_quiz_eligibility(self, user_address: str, quiz_score: int) -> Dict[str, Any]:
        """
        Verifica elegibilidade baseada em quiz
        Score >= 80: Pode registrar nomes premium/exclusive
        """
        eligibility = {
            "eligible": quiz_score >= 80,
            "score": quiz_score,
            "min_name_length": 6 if quiz_score < 80 else 3,
            "badge": None
        }

        if quiz_score >= 95:
            eligibility["badge"] = "flow-master"
            eligibility["discount"] = 0.5  # 50% desconto
        elif quiz_score >= 80:
            eligibility["badge"] = "flow-expert"
            eligibility["discount"] = 0.2  # 20% desconto

        return eligibility

    # ========== Comandos do Chat ==========

    def parse_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Detecta comandos FNS na mensagem do chat

        Comandos suportados:
        - resolve <nome>
        - check <nome>
        - register <nome>
        - profile <nome>
        - quiz start
        """
        message_lower = message.lower().strip()

        # Comando: resolve/endereço
        patterns = [
            (r'^(?:resolve|endereço de|endereco de)\s+(\S+)', 'resolve'),
            (r'^(?:check|verificar|disponível|disponivel)\s+(\S+)', 'check'),
            (r'^(?:register|registrar)\s+(\S+)', 'register'),
            (r'^(?:profile|perfil de|quem é|quem e)\s+(\S+)', 'profile'),
            (r'^quiz\s+(?:start|iniciar|começar)', 'quiz_start'),
        ]

        for pattern, action in patterns:
            match = re.match(pattern, message_lower)
            if match:
                if action == 'quiz_start':
                    return {"action": action}
                else:
                    name = match.group(1)
                    # Adiciona .find se não tiver
                    if not name.endswith('.find') and not name.endswith('.fn'):
                        name += '.find'
                    return {"action": action, "name": name}

        # Detecta menções a .find em mensagens gerais
        find_mentions = re.findall(r'(\w+\.find|\w+\.fn)', message_lower)
        if find_mentions:
            return {"action": "mention", "names": find_mentions}

        return None

    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Processa comando FNS detectado"""
        action = command["action"]

        if action == "resolve":
            address = await self.resolve_name(command["name"])
            return {
                "type": "resolve",
                "name": command["name"],
                "address": address,
                "success": address is not None
            }

        elif action == "check":
            available = await self.check_availability(command["name"])
            tier = self.get_name_tier(command["name"])
            fee = self.calculate_registration_fee(command["name"])

            return {
                "type": "availability",
                "name": command["name"],
                "available": available,
                "tier": tier.value,
                "fee": fee,
                "message": f"{'✅ Disponível' if available else '❌ Já registrado'}"
            }

        elif action == "profile":
            profile = await self.get_profile(command["name"])
            return {
                "type": "profile",
                "name": command["name"],
                "profile": profile,
                "success": profile is not None
            }

        elif action == "register":
            # Verificar disponibilidade primeiro
            available = await self.check_availability(command["name"])
            if not available:
                return {
                    "type": "register",
                    "success": False,
                    "error": "Nome já registrado"
                }

            validation = self.validate_name_format(command["name"])
            if not validation["valid"]:
                return {
                    "type": "register",
                    "success": False,
                    "error": validation["error"]
                }

            fee = self.calculate_registration_fee(command["name"])
            tier = self.get_name_tier(command["name"])
            sender_address = command.get("sender", "0x25f823e2a115b2dc")

            # Salvar no Neo4j se disponível
            if self.neo4j:
                try:
                    self.neo4j.save_name_registration(
                        name=validation["name"],
                        owner_address=sender_address,
                        buyer_address=sender_address,
                        tier=tier.value,
                        fee=fee,
                        transaction_id=f"pending_{datetime.now().timestamp()}"
                    )
                except Exception as e:
                    print(f"Erro ao salvar no Neo4j: {e}")

            return {
                "type": "register",
                "name": command["name"],
                "fee": fee,
                "tier": tier.value,
                "next_step": "confirm_payment",
                "saved_neo4j": self.neo4j is not None,
                "message": f"Para registrar {command['name']}, você precisa pagar {fee} FLOW. Digite 'confirmar' para prosseguir."
            }

        elif action == "quiz_start":
            return {
                "type": "quiz",
                "questions": self.get_quiz_questions(),
                "message": "🎯 Quiz FNS iniciado! Responda às perguntas para ganhar badges e descontos."
            }

        elif action == "mention":
            # Resolve todas as menções
            results = []
            for name in command["names"]:
                address = await self.resolve_name(name)
                results.append({"name": name, "address": address})

            return {
                "type": "mentions",
                "results": results
            }

        return {"type": "unknown", "action": action}

    def get_quiz_questions(self) -> List[Dict[str, Any]]:
        """Retorna questões do quiz FNS"""
        return [
            {
                "id": 1,
                "question": "Qual o tamanho mínimo de um nome .find?",
                "options": ["1 caractere", "2 caracteres", "3 caracteres", "4 caracteres"],
                "correct": 2
            },
            {
                "id": 2,
                "question": "Qual contrato gerencia os nomes .find na testnet?",
                "options": ["0x097bafa4e0b48eef", "0x35717efbbce11c74", "0x1234567890", "0xabcdef"],
                "correct": 1
            },
            {
                "id": 3,
                "question": "Quanto custa um nome de 3 caracteres na testnet?",
                "options": ["5 FLOW", "15 FLOW", "50 FLOW", "100 FLOW"],
                "correct": 2
            },
            {
                "id": 4,
                "question": "Nomes .find podem conter quais caracteres?",
                "options": ["Apenas letras", "Letras e números", "Letras, números e hífen", "Qualquer caractere"],
                "correct": 2
            },
            {
                "id": 5,
                "question": "O que é reverse lookup?",
                "options": [
                    "Buscar endereço por nome",
                    "Buscar nome por endereço",
                    "Reverter um registro",
                    "Lookup recursivo"
                ],
                "correct": 1
            }
        ]

    def format_response(self, result: Dict[str, Any]) -> str:
        """Formata resposta para exibição no chat"""
        response_type = result.get("type")

        if response_type == "resolve":
            if result["success"]:
                return f"📍 **{result['name']}** → `{result['address']}`"
            else:
                return f"❌ Nome **{result['name']}** não encontrado"

        elif response_type == "availability":
            msg = f"🔍 **{result['name']}**\n"
            msg += f"Status: {result['message']}\n"
            if result["available"]:
                msg += f"Tier: {result['tier'].upper()}\n"
                msg += f"Taxa: {result['fee']} FLOW"
            return msg

        elif response_type == "profile":
            if result["success"] and result["profile"]:
                profile = result["profile"]
                msg = f"👤 **Perfil de {result['name']}**\n"
                msg += f"Bio: {profile.get('bio', 'N/A')}\n"
                msg += f"Avatar: {profile.get('avatar', 'N/A')}\n"
                return msg
            else:
                return f"❌ Perfil de **{result['name']}** não encontrado"

        elif response_type == "register":
            return result.get("message", "Processando registro...")

        elif response_type == "quiz":
            msg = result["message"] + "\n\n"
            for q in result["questions"]:
                msg += f"**Q{q['id']}**: {q['question']}\n"
                for i, opt in enumerate(q['options']):
                    msg += f"  {chr(65+i)}. {opt}\n"
                msg += "\n"
            return msg

        elif response_type == "mentions":
            msg = "📎 **Nomes .find mencionados:**\n"
            for item in result["results"]:
                if item["address"]:
                    msg += f"• {item['name']} → `{item['address']}`\n"
                else:
                    msg += f"• {item['name']} → não registrado\n"
            return msg

        return str(result)


# ========== Integração com FastAPI ==========

async def setup_fns_endpoints(app):
    """Adiciona endpoints FNS ao servidor FastAPI"""
    from fastapi import HTTPException

    fns = FindNameService()

    @app.get("/api/fns/resolve/{name}")
    async def resolve_fns_name(name: str):
        """Resolve nome .find para endereço"""
        address = await fns.resolve_name(name)
        if address:
            return {
                "name": name,
                "address": address,
                "network": fns.config.network,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Nome {name} não encontrado")

    @app.get("/api/fns/check/{name}")
    async def check_fns_availability(name: str):
        """Verifica disponibilidade de nome"""
        validation = fns.validate_name_format(name)
        if not validation["valid"]:
            return {"available": False, "error": validation["error"]}

        available = await fns.check_availability(name)
        tier = fns.get_name_tier(name)
        fee = fns.calculate_registration_fee(name)

        return {
            "name": name,
            "available": available,
            "tier": tier.value,
            "fee": fee,
            "network": fns.config.network
        }

    @app.get("/api/fns/profile/{name}")
    async def get_fns_profile(name: str):
        """Obtém perfil de nome .find"""
        profile = await fns.get_profile(name)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail=f"Perfil {name} não encontrado")

    @app.post("/api/fns/quiz/submit")
    async def submit_fns_quiz(answers: dict):
        """Processa respostas do quiz FNS"""
        # Calcular score
        correct_answers = {1: 2, 2: 1, 3: 2, 4: 2, 5: 1}
        score = sum(1 for q_id, answer in answers.items()
                   if correct_answers.get(int(q_id)) == answer) * 20

        eligibility = await fns.check_quiz_eligibility("user_address", score)

        return {
            "score": score,
            "passed": score >= 80,
            "eligibility": eligibility
        }

    return fns


# ========== Exemplo de Uso ==========

async def main():
    """Demonstração do FNS"""
    fns = FindNameService()

    # Testar comandos
    test_messages = [
        "resolve flowverse.find",
        "check diego.find",
        "quem é andrea.find",
        "posso registrar test123.find?",
        "quiz start"
    ]

    print("=" * 60)
    print("🔍 Flow Name Service - Demonstração")
    print("=" * 60)

    for msg in test_messages:
        print(f"\n💬 Mensagem: '{msg}'")
        command = fns.parse_command(msg)

        if command:
            result = await fns.process_command(command)
            formatted = fns.format_response(result)
            print(f"📤 Resposta:\n{formatted}")
        else:
            print("❌ Comando não reconhecido")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())