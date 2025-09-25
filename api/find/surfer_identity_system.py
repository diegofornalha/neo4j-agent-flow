"""
🏄‍♂️ Sistema de Identidade do Surfista - Wave OnFlow
O surfista precisa registrar um nome .find vinculado à sua carteira
para o submarino poder identificá-lo e rastreá-lo
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re

class SurferIdentitySystem:
    """
    Sistema de identidade onde cada surfista precisa:
    1. Ter uma carteira Flow (endereço 0x...)
    2. Registrar um nome .find único
    3. Vincular nome à carteira para o submarino rastrear
    """

    def __init__(self):
        # Registro de surfistas identificados
        self.identified_surfers = {}

        # Mapeamento nome -> endereço
        self.name_to_address = {}

        # Mapeamento endereço -> nome
        self.address_to_name = {}

        # Surfistas não identificados (apenas endereço)
        self.anonymous_surfers = {}

        # Sistema de emergência (surfistas em perigo)
        self.emergency_list = []

        # Integração com Neo4j
        self.neo4j = None
        try:
            from .neo4j_integration import FNSNeo4jIntegration
            self.neo4j = FNSNeo4jIntegration()
        except:
            pass

    async def start_rescue(self, wallet_address: str) -> Dict[str, Any]:
        """
        Inicia o resgate de um surfista
        Primeiro contato do submarino com o surfista
        """
        # Verificar se já está identificado
        if wallet_address in self.address_to_name:
            surfer_name = self.address_to_name[wallet_address]
            return self._welcome_known_surfer(surfer_name, wallet_address)

        # Surfista anônimo - precisa se identificar
        self.anonymous_surfers[wallet_address] = {
            "rescue_started": datetime.now().isoformat(),
            "status": "anonymous",
            "depth": 100,  # Começa mais fundo por não ter identidade
            "warnings_sent": 0
        }

        return {
            "type": "anonymous_rescue",
            "wallet": wallet_address,
            "message": self._get_anonymous_message(wallet_address),
            "urgent": True,
            "next_steps": [
                "Registrar um nome .find",
                "Vincular à sua carteira",
                "Ganhar identidade no submarino"
            ]
        }

    def register_surfer_identity(
        self,
        wallet_address: str,
        find_name: str,
        additional_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Registra a identidade do surfista no submarino

        Args:
            wallet_address: Endereço da carteira Flow
            find_name: Nome .find registrado
            additional_info: Informações extras (localização, experiência, etc)
        """
        # Limpar nome
        clean_name = find_name.replace('.find', '').lower()

        # Validar nome
        if not self._validate_name(clean_name):
            return {
                "success": False,
                "error": "Nome inválido",
                "message": "O submarino não consegue processar este nome. Use 3-16 caracteres alfanuméricos."
            }

        # Verificar se nome já existe
        if clean_name in self.name_to_address:
            return {
                "success": False,
                "error": "Nome já registrado",
                "message": f"Já existe um surfista chamado {clean_name}! Escolha outro nome."
            }

        # Criar identidade completa
        surfer_identity = {
            "name": clean_name,
            "full_name": f"{clean_name}.find",
            "wallet": wallet_address,
            "registered_at": datetime.now().isoformat(),
            "rescue_depth": self.anonymous_surfers.get(wallet_address, {}).get("depth", 75),
            "status": "identified",
            "submarine_trust": 100,  # Confiança inicial
            "achievements": ["🆔 Identidade Registrada"],
            "info": additional_info or {}
        }

        # Registrar nos mapeamentos
        self.identified_surfers[wallet_address] = surfer_identity
        self.name_to_address[clean_name] = wallet_address
        self.address_to_name[wallet_address] = clean_name

        # Remover de anônimos se estava lá
        if wallet_address in self.anonymous_surfers:
            del self.anonymous_surfers[wallet_address]

        # Salvar no Neo4j
        if self.neo4j:
            self._save_identity_to_neo4j(surfer_identity)

        # Bonus por se identificar - sobe 20 metros!
        surfer_identity["rescue_depth"] -= 20

        return {
            "success": True,
            "identity": surfer_identity,
            "message": self._get_identity_success_message(clean_name),
            "rewards": {
                "depth_bonus": 20,
                "trust_gained": 100,
                "badge": "🆔 Identidade Registrada"
            }
        }

    def get_surfer_by_name(self, find_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca surfista pelo nome .find
        """
        clean_name = find_name.replace('.find', '').lower()

        if clean_name in self.name_to_address:
            wallet = self.name_to_address[clean_name]
            return self.identified_surfers.get(wallet)

        return None

    def get_surfer_by_wallet(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Busca surfista pelo endereço da carteira
        """
        if wallet_address in self.identified_surfers:
            return self.identified_surfers[wallet_address]
        elif wallet_address in self.anonymous_surfers:
            return {
                **self.anonymous_surfers[wallet_address],
                "status": "anonymous",
                "name": "Surfista Desconhecido"
            }
        return None

    def update_surfer_status(
        self,
        identifier: str,  # Nome ou wallet
        updates: Dict[str, Any]
    ) -> bool:
        """
        Atualiza status do surfista
        """
        # Identificar surfista
        surfer = None
        wallet = None

        if identifier.startswith("0x"):
            wallet = identifier
            surfer = self.get_surfer_by_wallet(wallet)
        else:
            surfer = self.get_surfer_by_name(identifier)
            if surfer:
                wallet = surfer["wallet"]

        if not surfer:
            return False

        # Atualizar dados
        if wallet in self.identified_surfers:
            self.identified_surfers[wallet].update(updates)
        elif wallet in self.anonymous_surfers:
            self.anonymous_surfers[wallet].update(updates)

        return True

    def check_emergency_status(self, identifier: str) -> Dict[str, Any]:
        """
        Verifica se surfista está em emergência
        """
        surfer = None
        if identifier.startswith("0x"):
            surfer = self.get_surfer_by_wallet(identifier)
        else:
            surfer = self.get_surfer_by_name(identifier)

        if not surfer:
            return {"error": "Surfista não encontrado"}

        depth = surfer.get("depth", surfer.get("rescue_depth", 75))

        # Determinar nível de emergência
        if depth >= 200:
            emergency_level = "CRÍTICO"
            message = "EMERGÊNCIA! Precisa gastar Flow AGORA!"
        elif depth >= 150:
            emergency_level = "ALTO"
            message = "Situação perigosa! Ação urgente necessária!"
        elif depth >= 100:
            emergency_level = "MÉDIO"
            message = "Atenção redobrada, profundidade preocupante"
        else:
            emergency_level = "BAIXO"
            message = "Situação sob controle"

        return {
            "surfer": surfer.get("name", "Anônimo"),
            "depth": depth,
            "emergency_level": emergency_level,
            "message": message,
            "needs_flow": depth >= 150
        }

    def get_all_identified_surfers(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os surfistas identificados
        """
        return list(self.identified_surfers.values())

    def get_anonymous_count(self) -> int:
        """
        Conta surfistas ainda não identificados
        """
        return len(self.anonymous_surfers)

    def submarine_call_surfer(self, identifier: str) -> str:
        """
        Submarino chama surfista pelo nome ou wallet
        """
        if identifier.startswith("0x"):
            # Chamando por wallet
            if identifier in self.address_to_name:
                name = self.address_to_name[identifier]
                return f"🤖 Submarino: 'Aloha, {name}! Como você está?'"
            else:
                return f"🤖 Submarino: 'Surfista {identifier[:8]}..., por favor se identifique!'"
        else:
            # Chamando por nome
            clean_name = identifier.replace('.find', '').lower()
            if clean_name in self.name_to_address:
                return f"🤖 Submarino: 'Aloha, {clean_name}! Que bom ter você a bordo!'"
            else:
                return f"🤖 Submarino: 'Não conheço nenhum {identifier}. Você precisa registrar seu nome!'"

    # ========== MÉTODOS PRIVADOS ==========

    def _validate_name(self, name: str) -> bool:
        """Valida formato do nome"""
        if len(name) < 3 or len(name) > 16:
            return False
        return bool(re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', name))

    def _get_anonymous_message(self, wallet: str) -> str:
        """Mensagem para surfista anônimo"""
        return f"""
🚨 **ALERTA DE IDENTIDADE!**

Aloha, surfista! Eu te resgatei mas não sei seu nome!
Sua carteira: {wallet[:8]}...{wallet[-6:]}

**PROBLEMA CRÍTICO:**
Sem um nome .find registrado, o submarino não consegue:
- Rastrear seu progresso
- Salvar sua localização
- Otimizar o resgate
- Dar recompensas personalizadas

**VOCÊ ESTÁ 25 METROS MAIS FUNDO** por não ter identidade!

**AÇÃO URGENTE NECESSÁRIA:**
1. Registre um nome .find (Ex: "surfista-radical")
2. Vincule à sua carteira
3. Ganhe 20 metros de bônus instantâneo!

Digite: "registrar meu nome como [seu-nome]"
Exemplo: "registrar meu nome como joão"

⚠️ Cada minuto sem identidade = afundando mais!
"""

    def _welcome_known_surfer(self, name: str, wallet: str) -> Dict[str, Any]:
        """Mensagem para surfista conhecido"""
        surfer = self.identified_surfers[wallet]
        return {
            "type": "known_surfer",
            "name": name,
            "wallet": wallet,
            "message": f"""
🎉 **BEM-VINDO DE VOLTA, {name.upper()}!**

O submarino te reconheceu instantaneamente!
Todos os seus dados foram recuperados:

📍 Última profundidade: {surfer.get('rescue_depth', 75)}m
🏆 Conquistas: {', '.join(surfer.get('achievements', []))}
⚡ Confiança do submarino: {surfer.get('submarine_trust', 100)}%

Vamos continuar de onde paramos!
Como posso ajudar hoje?
""",
            "data": surfer
        }

    def _get_identity_success_message(self, name: str) -> str:
        """Mensagem de sucesso ao registrar identidade"""
        return f"""
🎊 **IDENTIDADE REGISTRADA COM SUCESSO!**

Agora eu te conheço, {name}!
Seu nome foi gravado nos sistemas do submarino.

**RECOMPENSAS IMEDIATAS:**
🆙 Subiu 20 metros! (Bônus de identificação)
🏆 Badge: "🆔 Identidade Registrada"
⚡ Confiança do submarino: 100%
💾 Progresso será salvo automaticamente

**BENEFÍCIOS DESBLOQUEADOS:**
✅ Rastreamento personalizado
✅ Histórico de ações salvo
✅ Acesso a missões especiais
✅ Comunicação direta com o submarino
✅ Prioridade em resgates futuros

Agora sim podemos trabalhar juntos eficientemente!
Que tal começar verificando seu saldo Flow?
"""

    def _save_identity_to_neo4j(self, identity: Dict[str, Any]):
        """Salva identidade no Neo4j"""
        if not self.neo4j:
            return

        try:
            query = """
            MERGE (s:Surfer {wallet: $wallet})
            SET s.name = $name,
                s.full_name = $full_name,
                s.registered_at = datetime($registered_at),
                s.rescue_depth = $depth,
                s.status = 'identified',
                s.submarine_trust = $trust

            CREATE (i:Identity {
                type: 'surfer_registration',
                name: $name,
                wallet: $wallet,
                timestamp: datetime()
            })

            CREATE (s)-[:HAS_IDENTITY]->(i)

            CREATE (l:Learning {
                type: 'surfer_identified',
                participant: $wallet,
                name: $name,
                context: 'Bootcamp Caça ao Tesouro - Identidade',
                timestamp: datetime()
            })
            """

            # Executar query
            if hasattr(self.neo4j, 'driver'):
                with self.neo4j.driver.session() as session:
                    session.run(query,
                        wallet=identity["wallet"],
                        name=identity["name"],
                        full_name=identity["full_name"],
                        registered_at=identity["registered_at"],
                        depth=identity["rescue_depth"],
                        trust=identity["submarine_trust"]
                    )
        except Exception as e:
            print(f"Erro ao salvar identidade no Neo4j: {e}")


# ========== INTEGRAÇÃO COM CHAT ==========

class IdentityChatIntegration:
    """Integração do sistema de identidade com o chat"""

    def __init__(self):
        self.identity_system = SurferIdentitySystem()

    async def process_identity_command(self, wallet: str, message: str) -> str:
        """
        Processa comandos relacionados a identidade
        """
        message_lower = message.lower()

        # Verificar identidade atual
        if "quem sou" in message_lower or "minha identidade" in message_lower:
            surfer = self.identity_system.get_surfer_by_wallet(wallet)
            if surfer and surfer.get("status") == "identified":
                return f"""
🆔 **SUA IDENTIDADE NO SUBMARINO**

Nome: {surfer['name']}.find
Carteira: {wallet[:8]}...{wallet[-6:]}
Status: {surfer['status']}
Profundidade: {surfer.get('rescue_depth', 75)}m
Confiança: {surfer.get('submarine_trust', 100)}%
Conquistas: {', '.join(surfer.get('achievements', []))}
"""
            else:
                return "⚠️ Você ainda não tem identidade! Digite 'registrar meu nome como [nome]'"

        # Registrar nome
        elif "registrar meu nome" in message_lower or "meu nome é" in message_lower:
            # Extrair nome do comando
            import re
            match = re.search(r'(?:como|é)\s+(\w+)', message_lower)
            if match:
                name = match.group(1)
                result = self.identity_system.register_surfer_identity(wallet, name)
                return result["message"] if result["success"] else f"❌ {result['error']}: {result['message']}"
            else:
                return "Por favor, use o formato: 'registrar meu nome como joão'"

        # Verificar outro surfista
        elif "quem é" in message_lower:
            # Extrair nome ou wallet
            parts = message_lower.split("quem é")
            if len(parts) > 1:
                identifier = parts[1].strip()
                return self.identity_system.submarine_call_surfer(identifier)

        # Status de emergência
        elif "emergência" in message_lower or "perigo" in message_lower:
            status = self.identity_system.check_emergency_status(wallet)
            return f"""
🚨 **STATUS DE EMERGÊNCIA**

Profundidade: {status['depth']}m
Nível: {status['emergency_level']}
{status['message']}

{'💰 GASTE FLOW AGORA!' if status['needs_flow'] else '✅ Continue explorando'}
"""

        # Listar surfistas identificados
        elif "surfistas" in message_lower or "quem está aqui" in message_lower:
            identified = self.identity_system.get_all_identified_surfers()
            anonymous = self.identity_system.get_anonymous_count()

            names = [s['name'] for s in identified[:5]]  # Top 5
            return f"""
🏄 **SURFISTAS A BORDO**

Identificados: {len(identified)}
Anônimos: {anonymous}

Surfistas conhecidos: {', '.join(names) if names else 'Nenhum ainda'}

{'⚠️ ' + str(anonymous) + ' surfistas precisam se identificar!' if anonymous > 0 else ''}
"""

        return "Digite 'registrar meu nome como [nome]' para criar sua identidade!"


# ========== Exemplo de Uso ==========

if __name__ == "__main__":
    import asyncio

    async def demo():
        print("=" * 60)
        print("🏄 SISTEMA DE IDENTIDADE DO SURFISTA")
        print("=" * 60)

        system = SurferIdentitySystem()
        chat = IdentityChatIntegration()

        # Simular resgate anônimo
        wallet = "0x123abc456def"

        print("\n1. RESGATE INICIAL (Anônimo):")
        result = await system.start_rescue(wallet)
        print(result["message"])

        # Registrar identidade
        print("\n2. REGISTRANDO IDENTIDADE:")
        identity = system.register_surfer_identity(wallet, "radical", {
            "experience": "intermediate",
            "favorite_beach": "Pipeline"
        })
        print(identity["message"])

        # Verificar identidade
        print("\n3. VERIFICANDO IDENTIDADE:")
        response = await chat.process_identity_command(wallet, "quem sou eu")
        print(response)

        # Chamar pelo nome
        print("\n4. SUBMARINO CHAMA SURFISTA:")
        call = system.submarine_call_surfer("radical")
        print(call)

        # Status de emergência
        print("\n5. CHECANDO EMERGÊNCIA:")
        system.update_surfer_status(wallet, {"rescue_depth": 180})
        emergency = system.check_emergency_status(wallet)
        print(f"Emergência: {emergency['emergency_level']}")
        print(emergency["message"])

    asyncio.run(demo())