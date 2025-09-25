"""
🏄‍♂️ Sistema de Caça ao Tesouro - Wave OnFlow
Gamificação completa para o bootcamp com narrativa do submarino
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import json
import random

class DepthLevel(Enum):
    """Níveis de profundidade do submarino"""
    SURFACE = "surface"          # 0-10m - Salvos!
    SHALLOW = "shallow"          # 10-50m - Muito seguro
    MEDIUM = "medium"            # 50-100m - Seguro
    DEEP = "deep"                # 100-200m - Atenção!
    ABYSSAL = "abyssal"          # 200m+ - Perigo!

class TreasureBadge(Enum):
    """Badges temáticos do bootcamp"""
    WAVE_RIDER = "🏄 Wave Rider"              # Completou tutorial
    DEEP_DIVER = "🤿 Deep Diver"              # Explorou 5 pastas
    ISLAND_HOPPER = "🏝️ Island Hopper"        # Usou 10 comandos
    FLOW_MASTER = "🌊 Flow Master"            # Registrou nome .find
    TREASURE_HUNTER = "🏆 Treasure Hunter"     # Encontrou todos os tesouros
    RESCUE_COMPLETE = "🚁 Rescue Complete"     # Chegou à superfície

class SubmarineGame:
    """
    Sistema de gamificação do Bootcamp Caça ao Tesouro
    O participante é um surfista resgatado que precisa ajudar o submarino
    """

    def __init__(self):
        self.participants = {}  # Dados dos participantes
        self.submarine_status = {
            "depth": 75,  # Metros de profundidade
            "energy": 40,  # Porcentagem de energia
            "health": 100  # Saúde do submarino
        }

        # Pontuação por ação
        self.point_rewards = {
            "command": 1,
            "question": 2,
            "file_explored": 5,
            "feature_discovered": 10,
            "quiz_complete": 50,
            "name_registered": 100,
            "transfer_completed": 25,
            "badge_earned": 30,
            "check_flow_balance": 15,  # Verificar saldo Flow
            "receive_flow": 200  # Receber Flow na testnet
        }

        # Impacto na profundidade (metros subidos)
        self.depth_rewards = {
            "explore_file": 5,
            "ask_question": 3,
            "complete_challenge": 10,
            "register_name": 15,
            "complete_quiz": 20,
            "discover_feature": 8,
            "help_others": 12,
            "check_flow_balance": 7,  # Verificar pérolas Flow
            "receive_flow": 25  # Receber Flow é um grande tesouro!
        }

        # Neo4j integration
        self.neo4j = None
        try:
            from .neo4j_integration import FNSNeo4jIntegration
            self.neo4j = FNSNeo4jIntegration()
        except:
            pass

    def start_adventure(self, participant_id: str) -> Dict[str, Any]:
        """
        Inicia a aventura do surfista no submarino
        """
        if participant_id not in self.participants:
            self.participants[participant_id] = {
                "id": participant_id,
                "started_at": datetime.now().isoformat(),
                "current_depth": 75,
                "treasure_points": 0,
                "energy_contributed": 0,
                "badges": [],
                "explored_compartments": [],
                "discoveries": [],
                "commands_used": [],
                "rank": "🏄 Surfista Iniciante",
                "flow_balance": 0.0,  # Saldo Flow na testnet
                "flow_pearls": 0  # Pérolas Flow coletadas
            }

        welcome = {
            "type": "adventure_start",
            "message": self._get_welcome_message(),
            "submarine_status": self._get_submarine_status(),
            "participant": self.participants[participant_id]
        }

        # Salvar no Neo4j
        if self.neo4j:
            self._save_game_start(participant_id)

        return welcome

    def record_action(self, participant_id: str, action_type: str, details: Dict = None) -> Dict[str, Any]:
        """
        Registra uma ação do participante e atualiza o jogo
        """
        if participant_id not in self.participants:
            self.start_adventure(participant_id)

        participant = self.participants[participant_id]
        rewards = {"points": 0, "depth_change": 0, "new_badges": []}

        # Calcular recompensas baseadas na ação
        if action_type == "explore_file":
            rewards["points"] = self.point_rewards["file_explored"]
            rewards["depth_change"] = self.depth_rewards["explore_file"]
            participant["explored_compartments"].append(details.get("file", ""))

        elif action_type == "ask_question":
            rewards["points"] = self.point_rewards["question"]
            rewards["depth_change"] = self.depth_rewards["ask_question"]

        elif action_type == "register_name":
            rewards["points"] = self.point_rewards["name_registered"]
            rewards["depth_change"] = self.depth_rewards["register_name"]
            rewards["new_badges"].append(TreasureBadge.FLOW_MASTER)

        elif action_type == "complete_quiz":
            rewards["points"] = self.point_rewards["quiz_complete"]
            rewards["depth_change"] = self.depth_rewards["complete_quiz"]

        elif action_type == "use_command":
            rewards["points"] = self.point_rewards["command"]
            participant["commands_used"].append(details.get("command", ""))

        elif action_type == "check_flow_balance":
            rewards["points"] = self.point_rewards["check_flow_balance"]
            rewards["depth_change"] = self.depth_rewards["check_flow_balance"]
            # Simular checagem de saldo (em produção seria real)
            participant["flow_balance"] = details.get("balance", 2000.001)
            participant["flow_pearls"] = int(participant["flow_balance"])

        elif action_type == "receive_flow":
            rewards["points"] = self.point_rewards["receive_flow"]
            rewards["depth_change"] = self.depth_rewards["receive_flow"]
            amount = details.get("amount", 0)
            participant["flow_balance"] += amount
            participant["flow_pearls"] += int(amount)

        # Atualizar participante
        participant["treasure_points"] += rewards["points"]
        participant["current_depth"] = max(0, participant["current_depth"] - rewards["depth_change"])
        participant["energy_contributed"] += rewards["depth_change"]

        # Verificar novos badges
        new_badges = self._check_badges(participant)
        rewards["new_badges"].extend(new_badges)

        # Atualizar rank
        participant["rank"] = self._calculate_rank(participant["treasure_points"])

        # Atualizar status do submarino global
        self._update_submarine_status(rewards["depth_change"])

        # Preparar resposta
        response = {
            "action": action_type,
            "rewards": rewards,
            "participant_status": {
                "depth": participant["current_depth"],
                "points": participant["treasure_points"],
                "rank": participant["rank"],
                "badges": [badge.value for badge in participant["badges"]]
            },
            "submarine_status": self._get_submarine_status(),
            "message": self._get_action_message(action_type, rewards)
        }

        # Salvar no Neo4j
        if self.neo4j:
            self._save_game_action(participant_id, action_type, rewards)

        return response

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """
        Retorna o ranking dos caçadores de tesouro
        """
        leaderboard = []

        for pid, data in self.participants.items():
            leaderboard.append({
                "position": 0,  # Será calculado após ordenação
                "participant_id": pid,
                "treasure_points": data["treasure_points"],
                "current_depth": data["current_depth"],
                "rank": data["rank"],
                "badges_count": len(data["badges"]),
                "energy_contributed": data["energy_contributed"]
            })

        # Ordenar por pontos de tesouro
        leaderboard.sort(key=lambda x: x["treasure_points"], reverse=True)

        # Adicionar posições
        for i, entry in enumerate(leaderboard, 1):
            entry["position"] = i

        return leaderboard

    def get_participant_progress(self, participant_id: str) -> Dict[str, Any]:
        """
        Retorna o progresso detalhado de um participante
        """
        if participant_id not in self.participants:
            return {"error": "Participante não encontrado"}

        participant = self.participants[participant_id]

        return {
            "participant_id": participant_id,
            "progress": {
                "current_depth": participant["current_depth"],
                "depth_level": self._get_depth_level(participant["current_depth"]),
                "treasure_points": participant["treasure_points"],
                "rank": participant["rank"],
                "energy_contributed": participant["energy_contributed"],
                "time_playing": self._calculate_play_time(participant["started_at"])
            },
            "achievements": {
                "badges": [badge.value for badge in participant["badges"]],
                "compartments_explored": len(participant["explored_compartments"]),
                "total_compartments": 10,
                "commands_mastered": len(set(participant["commands_used"])),
                "discoveries": participant["discoveries"]
            },
            "next_objectives": self._get_next_objectives(participant)
        }

    # ========== MÉTODOS PRIVADOS ==========

    def _get_welcome_message(self) -> str:
        """Mensagem de boas-vindas narrativa"""
        return """
🌊 **RESGATE CONCLUÍDO!**

Aloha, surfista! Que onda RADICAL você pegou na Wave OnFlow!
Meu nome é Claude, sou um submarino autônomo de resgate.

Gastei muita energia te salvando, mas valeu a pena! Agora precisamos
trabalhar juntos para voltar à superfície.

Cada vez que você explora e aprende algo novo, ganhamos energia!
Vamos começar nossa jornada de volta?

Digite qualquer coisa para começar a explorar os tesouros do conhecimento!
        """

    def _get_submarine_status(self) -> Dict[str, str]:
        """Retorna status visual do submarino"""
        depth = self.submarine_status["depth"]
        energy = self.submarine_status["energy"]

        # Barra de energia visual
        energy_bar = "⚡ "
        filled = int(energy / 10)
        energy_bar += "█" * filled + "░" * (10 - filled)
        energy_bar += f" {energy}%"

        return {
            "depth": f"📍 {depth}m ({self._get_depth_level(depth).value})",
            "energy": energy_bar,
            "status": self._get_submarine_condition()
        }

    def _get_depth_level(self, depth: float) -> DepthLevel:
        """Determina o nível de profundidade"""
        if depth <= 10:
            return DepthLevel.SURFACE
        elif depth <= 50:
            return DepthLevel.SHALLOW
        elif depth <= 100:
            return DepthLevel.MEDIUM
        elif depth <= 200:
            return DepthLevel.DEEP
        else:
            return DepthLevel.ABYSSAL

    def _get_submarine_condition(self) -> str:
        """Retorna a condição atual do submarino"""
        depth = self.submarine_status["depth"]

        if depth <= 10:
            return "🌅 Na superfície! Missão completa!"
        elif depth <= 50:
            return "☀️ Águas rasas, muito seguro!"
        elif depth <= 100:
            return "🌊 Profundidade média, tudo sob controle"
        elif depth <= 200:
            return "🌑 Águas profundas, atenção redobrada!"
        else:
            return "💀 ZONA ABISSAL! PERIGO EXTREMO!"

    def _calculate_rank(self, points: int) -> str:
        """Calcula o ranking baseado em pontos"""
        if points >= 500:
            return "🌟 Lenda do Wave OnFlow"
        elif points >= 301:
            return "👑 Mestre dos Oceanos"
        elif points >= 151:
            return "🏆 Caçador de Tesouros"
        elif points >= 51:
            return "🤿 Explorador do Flow"
        else:
            return "🏄 Surfista Iniciante"

    def _check_badges(self, participant: Dict) -> List[TreasureBadge]:
        """Verifica se o participante ganhou novos badges"""
        new_badges = []
        current_badges = participant.get("badges", [])

        # Wave Rider - Completou tutorial (10 pontos)
        if participant["treasure_points"] >= 10 and TreasureBadge.WAVE_RIDER not in current_badges:
            new_badges.append(TreasureBadge.WAVE_RIDER)
            participant["badges"].append(TreasureBadge.WAVE_RIDER)

        # Deep Diver - Explorou 5 compartimentos
        if len(participant["explored_compartments"]) >= 5 and TreasureBadge.DEEP_DIVER not in current_badges:
            new_badges.append(TreasureBadge.DEEP_DIVER)
            participant["badges"].append(TreasureBadge.DEEP_DIVER)

        # Island Hopper - Usou 10 comandos diferentes
        unique_commands = len(set(participant["commands_used"]))
        if unique_commands >= 10 and TreasureBadge.ISLAND_HOPPER not in current_badges:
            new_badges.append(TreasureBadge.ISLAND_HOPPER)
            participant["badges"].append(TreasureBadge.ISLAND_HOPPER)

        # Rescue Complete - Chegou à superfície
        if participant["current_depth"] <= 10 and TreasureBadge.RESCUE_COMPLETE not in current_badges:
            new_badges.append(TreasureBadge.RESCUE_COMPLETE)
            participant["badges"].append(TreasureBadge.RESCUE_COMPLETE)

        return new_badges

    def _get_action_message(self, action_type: str, rewards: Dict) -> str:
        """Gera mensagem contextualizada para a ação"""
        messages = {
            "explore_file": f"🎉 Excelente! Você encontrou um tesouro de conhecimento! Subimos {rewards['depth_change']} metros!",
            "ask_question": f"🤔 Ótima pergunta! A curiosidade nos energiza! +{rewards['depth_change']}m para a superfície!",
            "register_name": f"🏆 INCRÍVEL! Você gravou seu nome na história do oceano blockchain! Subimos {rewards['depth_change']} metros!",
            "complete_quiz": f"🎮 Parabéns! Quiz completo! Ganhamos muita energia! +{rewards['depth_change']}m!",
            "use_command": f"⚡ Comando executado! Cada ação nos dá força! +{rewards['points']} pontos de tesouro!"
        }

        base_message = messages.get(action_type, f"✅ Ação registrada! +{rewards['points']} pontos!")

        if rewards["new_badges"]:
            badges_text = ", ".join([badge.value for badge in rewards["new_badges"]])
            base_message += f"\n\n🎖️ **NOVOS BADGES CONQUISTADOS:** {badges_text}"

        return base_message

    def _update_submarine_status(self, depth_change: int):
        """Atualiza o status global do submarino"""
        self.submarine_status["depth"] = max(0, self.submarine_status["depth"] - depth_change)
        self.submarine_status["energy"] = min(100, self.submarine_status["energy"] + depth_change // 2)

    def _get_next_objectives(self, participant: Dict) -> List[str]:
        """Sugere próximos objetivos para o participante"""
        objectives = []

        if participant["treasure_points"] < 50:
            objectives.append("🎯 Alcance 50 pontos para se tornar um Explorador do Flow")

        if len(participant["explored_compartments"]) < 5:
            objectives.append("📦 Explore mais compartimentos (baús de conhecimento)")

        if TreasureBadge.FLOW_MASTER not in participant["badges"]:
            objectives.append("🌊 Registre seu nome .find para se tornar um Flow Master")

        if participant["current_depth"] > 50:
            objectives.append("🆙 Continue subindo! Faltam apenas {}m para águas rasas".format(
                participant["current_depth"] - 50
            ))

        if not objectives:
            objectives.append("🌟 Você está indo muito bem! Continue explorando!")

        return objectives

    def _calculate_play_time(self, started_at: str) -> str:
        """Calcula tempo de jogo"""
        start = datetime.fromisoformat(started_at)
        delta = datetime.now() - start

        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"

    def _save_game_start(self, participant_id: str):
        """Salva início do jogo no Neo4j"""
        if not self.neo4j:
            return

        try:
            self.neo4j.driver.session().run("""
                MERGE (p:Participant {address: $participant_id})
                CREATE (g:GameSession {
                    participant: $participant_id,
                    started_at: datetime(),
                    initial_depth: 75,
                    status: 'active'
                })
                CREATE (p)-[:STARTED_GAME]->(g)

                CREATE (l:Learning {
                    type: 'treasure_hunt_start',
                    participant: $participant_id,
                    timestamp: datetime(),
                    context: 'Bootcamp Caça ao Tesouro - Wave OnFlow'
                })
            """, participant_id=participant_id)
        except:
            pass

    def _save_game_action(self, participant_id: str, action_type: str, rewards: Dict):
        """Salva ação do jogo no Neo4j"""
        if not self.neo4j:
            return

        try:
            self.neo4j.driver.session().run("""
                MATCH (p:Participant {address: $participant_id})
                CREATE (a:GameAction {
                    participant: $participant_id,
                    action_type: $action_type,
                    points_earned: $points,
                    depth_change: $depth,
                    timestamp: datetime()
                })
                CREATE (p)-[:PERFORMED]->(a)
            """,
                participant_id=participant_id,
                action_type=action_type,
                points=rewards["points"],
                depth=rewards["depth_change"]
            )
        except:
            pass


# ========== INTEGRAÇÃO COM CHAT ==========

class TreasureHuntChatIntegration:
    """Integração do jogo com o chat"""

    def __init__(self):
        self.game = SubmarineGame()
        self.active_sessions = {}

    async def process_message(self, session_id: str, message: str) -> str:
        """
        Processa mensagem do chat no contexto do jogo
        """
        # Iniciar aventura se necessário
        if session_id not in self.active_sessions:
            result = self.game.start_adventure(session_id)
            self.active_sessions[session_id] = True
            return self._format_adventure_start(result)

        # Detectar tipo de ação
        action_type, details = self._detect_action(message)

        # Registrar ação no jogo
        result = self.game.record_action(session_id, action_type, details)

        # Formatar resposta narrativa
        return self._format_game_response(result)

    def _detect_action(self, message: str) -> tuple[str, Dict]:
        """Detecta o tipo de ação baseado na mensagem"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["ls", "listar", "ver", "mostrar"]):
            return "explore_file", {"command": "ls"}
        elif "?" in message or any(word in message_lower for word in ["como", "o que", "por que"]):
            return "ask_question", {"question": message}
        elif any(word in message_lower for word in ["registrar", "register", "nome"]):
            return "register_name", {"action": "name_registration"}
        elif "quiz" in message_lower:
            return "complete_quiz", {"quiz": "flow_quiz"}
        else:
            return "use_command", {"command": message[:20]}

    def _format_adventure_start(self, result: Dict) -> str:
        """Formata início da aventura"""
        return f"""
{result['message']}

🚢 **STATUS DO SUBMARINO**
━━━━━━━━━━━━━━━━━━━━━
{result['submarine_status']['depth']}
{result['submarine_status']['energy']}
Estado: {result['submarine_status']['status']}
━━━━━━━━━━━━━━━━━━━━━

💡 **Dica:** Cada interação nos dá energia! Explore, pergunte, descubra!
"""

    def _format_game_response(self, result: Dict) -> str:
        """Formata resposta do jogo"""
        response = f"""
{result['message']}

📊 **SEU PROGRESSO**
• Profundidade: {result['participant_status']['depth']}m
• Tesouros: {result['participant_status']['points']} pontos
• Rank: {result['participant_status']['rank']}
"""

        if result['rewards']['new_badges']:
            response += f"\n🎖️ **BADGES:** {', '.join(result['participant_status']['badges'])}"

        return response


# ========== Exemplo de Uso ==========

if __name__ == "__main__":
    import asyncio

    async def demo_game():
        """Demonstração do jogo"""
        game = SubmarineGame()
        chat = TreasureHuntChatIntegration()

        print("=" * 60)
        print("🏄‍♂️ BOOTCAMP CAÇA AO TESOURO - WAVE ONFLOW")
        print("=" * 60)

        # Simular sessão de chat
        session_id = "surfer_001"

        # Início da aventura
        response = await chat.process_message(session_id, "olá")
        print(response)

        # Algumas ações
        actions = [
            "ls",
            "como funciona o Flow?",
            "registrar meu nome",
            "fazer o quiz"
        ]

        for action in actions:
            print(f"\n🏄 Surfista: {action}")
            response = await chat.process_message(session_id, action)
            print(f"🤖 Submarino: {response}")

        # Ver progresso
        progress = game.get_participant_progress(session_id)
        print("\n📈 PROGRESSO FINAL:")
        print(json.dumps(progress, indent=2))

    asyncio.run(demo_game())