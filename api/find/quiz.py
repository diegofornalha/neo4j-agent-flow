"""
Sistema de Quiz e Badges para FNS
Gamificação para desbloquear nomes premium e exclusivos
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# Importar integração Neo4j
try:
    from .neo4j_integration import FNSNeo4jIntegration
except ImportError:
    FNSNeo4jIntegration = None

@dataclass
class QuizQuestion:
    """Questão do quiz FNS"""
    id: int
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    points: int = 20

class FNSQuiz:
    """Sistema de quiz para Flow Name Service"""

    def __init__(self):
        self.questions = self._load_questions()
        self.user_scores = {}  # Cache de scores por usuário

        # Inicializar Neo4j se disponível
        self.neo4j = None
        if FNSNeo4jIntegration:
            try:
                self.neo4j = FNSNeo4jIntegration()
            except Exception as e:
                print(f"⚠️ Neo4j não disponível para Quiz: {e}")

    def _load_questions(self) -> List[QuizQuestion]:
        """Carrega questões do quiz"""
        return [
            QuizQuestion(
                id=1,
                question="Qual o tamanho mínimo de um nome .find?",
                options=[
                    "1 caractere",
                    "2 caracteres",
                    "3 caracteres",
                    "4 caracteres"
                ],
                correct_answer=2,
                explanation="Nomes .find devem ter no mínimo 3 caracteres para evitar conflitos e spam.",
                points=20
            ),
            QuizQuestion(
                id=2,
                question="Qual contrato gerencia os nomes .find na TESTNET?",
                options=[
                    "0x097bafa4e0b48eef",
                    "0x35717efbbce11c74",
                    "0x1234567890abcdef",
                    "0xdeadbeef"
                ],
                correct_answer=1,
                explanation="Na testnet, o contrato FIND está em 0x35717efbbce11c74.",
                points=20
            ),
            QuizQuestion(
                id=3,
                question="Quanto custa um nome EXCLUSIVO (≤3 chars) na testnet?",
                options=[
                    "5 FLOW",
                    "15 FLOW",
                    "50 FLOW",
                    "100 FLOW"
                ],
                correct_answer=2,
                explanation="Nomes exclusivos de 3 caracteres ou menos custam 50 FLOW na testnet.",
                points=20
            ),
            QuizQuestion(
                id=4,
                question="Quais caracteres são permitidos em nomes .find?",
                options=[
                    "Apenas letras minúsculas",
                    "Letras e números",
                    "Letras minúsculas, números e hífen",
                    "Qualquer caractere ASCII"
                ],
                correct_answer=2,
                explanation="Nomes .find podem conter letras minúsculas (a-z), números (0-9) e hífen (-).",
                points=20
            ),
            QuizQuestion(
                id=5,
                question="O que é 'reverse lookup' no contexto FNS?",
                options=[
                    "Buscar endereço a partir do nome",
                    "Buscar nome a partir do endereço",
                    "Reverter um registro de nome",
                    "Lookup em ordem alfabética reversa"
                ],
                correct_answer=1,
                explanation="Reverse lookup permite encontrar o nome .find associado a um endereço Flow.",
                points=20
            ),
            # Questões bônus avançadas
            QuizQuestion(
                id=6,
                question="Como o FNS garante que nomes sejam únicos?",
                options=[
                    "Base de dados centralizada",
                    "Recursos não-fungíveis na blockchain",
                    "Verificação manual",
                    "Sistema de votação"
                ],
                correct_answer=1,
                explanation="FNS usa recursos NFT do Cadence que são naturalmente únicos e não-duplicáveis.",
                points=25
            ),
            QuizQuestion(
                id=7,
                question="Qual a vantagem de usar .find sobre endereços hex?",
                options=[
                    "Mais seguro",
                    "Mais rápido",
                    "Legível e memorável",
                    "Menor taxa de gas"
                ],
                correct_answer=2,
                explanation="Nomes .find são legíveis e fáceis de memorizar, melhorando a UX.",
                points=15
            )
        ]

    def start_quiz(self, user_id: str) -> Dict[str, Any]:
        """Inicia um novo quiz para o usuário"""
        return {
            "quiz_id": f"quiz_{user_id}_{datetime.now().timestamp()}",
            "user_id": user_id,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "options": q.options
                }
                for q in self.questions[:5]  # Primeiras 5 questões obrigatórias
            ],
            "started_at": datetime.now().isoformat(),
            "time_limit_minutes": 10
        }

    def submit_answers(self, user_id: str, answers: Dict[int, int]) -> Dict[str, Any]:
        """
        Processa respostas do quiz

        Args:
            user_id: ID do usuário
            answers: Dict com {question_id: answer_index}

        Returns:
            Resultado com score, badge e benefícios
        """
        correct = 0
        total_points = 0
        max_points = 0
        details = []

        for question in self.questions:
            if question.id in answers:
                max_points += question.points
                user_answer = answers[question.id]
                is_correct = user_answer == question.correct_answer

                if is_correct:
                    correct += 1
                    total_points += question.points

                details.append({
                    "question_id": question.id,
                    "correct": is_correct,
                    "user_answer": user_answer,
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation if not is_correct else None
                })

        # Calcular percentual
        score_percent = (total_points / max_points * 100) if max_points > 0 else 0

        # Determinar badge e benefícios
        badge, benefits = self._calculate_rewards(score_percent)

        # Salvar score
        self.user_scores[user_id] = {
            "score": score_percent,
            "badge": badge,
            "timestamp": datetime.now().isoformat()
        }

        # Salvar no Neo4j se disponível
        if self.neo4j:
            try:
                self.neo4j.save_quiz_result(
                    participant_address=user_id,
                    score=int(score_percent),
                    badge=badge,
                    discount=benefits.get("discount", 0),
                    answers=answers
                )
            except Exception as e:
                print(f"Erro ao salvar quiz no Neo4j: {e}")

        return {
            "user_id": user_id,
            "score": score_percent,
            "correct": correct,
            "total": len(answers),
            "points": total_points,
            "max_points": max_points,
            "passed": score_percent >= 80,
            "badge": badge,
            "benefits": benefits,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_rewards(self, score: float) -> tuple[Optional[str], Dict[str, Any]]:
        """Calcula badge e benefícios baseados no score"""
        if score >= 95:
            return "flow-master", {
                "discount": 0.5,  # 50% desconto
                "min_name_length": 3,
                "tier_access": ["exclusive", "premium", "standard"],
                "special_perks": ["Early access", "NFT badge", "Priority support"]
            }
        elif score >= 80:
            return "flow-expert", {
                "discount": 0.2,  # 20% desconto
                "min_name_length": 3,
                "tier_access": ["premium", "standard"],
                "special_perks": ["Badge NFT"]
            }
        else:
            return None, {
                "discount": 0,
                "min_name_length": 6,
                "tier_access": ["standard"],
                "special_perks": []
            }

    def get_user_badge(self, user_id: str) -> Optional[str]:
        """Retorna badge do usuário se existir"""
        if user_id in self.user_scores:
            return self.user_scores[user_id].get("badge")
        return None

    def verify_eligibility(self, user_id: str, name_length: int) -> Dict[str, Any]:
        """Verifica se usuário pode registrar nome baseado em badges"""
        badge = self.get_user_badge(user_id)

        if not badge:
            # Sem badge - apenas nomes standard
            return {
                "eligible": name_length >= 6,
                "reason": "Complete o quiz com 80%+ para nomes premium",
                "min_length": 6
            }

        if badge == "flow-master":
            # Master - qualquer nome
            return {
                "eligible": name_length >= 3,
                "reason": "Badge flow-master: acesso total",
                "min_length": 3,
                "discount": 0.5
            }

        if badge == "flow-expert":
            # Expert - nomes premium e standard
            return {
                "eligible": name_length >= 3,
                "reason": "Badge flow-expert: nomes premium desbloqueados",
                "min_length": 3,
                "discount": 0.2
            }

        return {
            "eligible": False,
            "reason": "Badge inválido"
        }

    def format_quiz_for_chat(self) -> str:
        """Formata questões do quiz para exibição no chat"""
        output = "🎯 **Quiz Flow Name Service**\n\n"
        output += "Responda corretamente para desbloquear benefícios:\n"
        output += "• 80%+ = Badge Expert (20% desconto)\n"
        output += "• 95%+ = Badge Master (50% desconto)\n\n"

        for i, q in enumerate(self.questions[:5], 1):
            output += f"**Q{i}**: {q.question}\n"
            for j, option in enumerate(q.options):
                output += f"  {chr(65+j)}. {option}\n"
            output += "\n"

        output += "Digite suas respostas no formato: `quiz submit A,B,C,D,E`"
        return output

    def parse_quiz_response(self, response: str) -> Optional[Dict[int, int]]:
        """
        Parse resposta do usuário no formato 'A,B,C,D,E'

        Returns:
            Dict com {question_id: answer_index} ou None se inválido
        """
        try:
            # Remove espaços e converte para maiúscula
            response = response.upper().replace(" ", "")

            # Split por vírgula
            answers_str = response.split(",")

            # Converter letras para índices
            answers = {}
            for i, answer in enumerate(answers_str, 1):
                if answer in "ABCD":
                    answers[i] = ord(answer) - ord('A')
                else:
                    return None

            return answers
        except:
            return None


# ========== Integração com Chat ==========

class QuizChatIntegration:
    """Integração do quiz com o sistema de chat"""

    def __init__(self):
        self.quiz = FNSQuiz()
        self.active_quizzes = {}  # user_id -> quiz_data

    async def handle_quiz_command(self, user_id: str, command: str) -> str:
        """Processa comandos de quiz do chat"""
        parts = command.lower().split()

        if len(parts) < 2:
            return "Comandos: `quiz start` ou `quiz submit A,B,C,D,E`"

        action = parts[1]

        if action == "start" or action == "iniciar":
            # Iniciar novo quiz
            quiz_data = self.quiz.start_quiz(user_id)
            self.active_quizzes[user_id] = quiz_data
            return self.quiz.format_quiz_for_chat()

        elif action == "submit" or action == "enviar":
            # Processar respostas
            if user_id not in self.active_quizzes:
                return "❌ Você não tem um quiz ativo. Digite `quiz start` para começar."

            if len(parts) < 3:
                return "❌ Formato: `quiz submit A,B,C,D,E`"

            # Parse respostas
            answers_str = " ".join(parts[2:])
            answers = self.quiz.parse_quiz_response(answers_str)

            if not answers:
                return "❌ Formato inválido. Use: `quiz submit A,B,C,D,E`"

            # Processar e retornar resultado
            result = self.quiz.submit_answers(user_id, answers)

            # Limpar quiz ativo
            del self.active_quizzes[user_id]

            # Formatar resposta
            return self._format_quiz_result(result)

        elif action == "status":
            # Verificar badge atual
            badge = self.quiz.get_user_badge(user_id)
            if badge:
                return f"🏆 Seu badge atual: **{badge}**"
            else:
                return "📝 Você ainda não tem badge. Complete o quiz para ganhar!"

        return "❓ Comando não reconhecido. Use: `quiz start`, `quiz submit` ou `quiz status`"

    def _format_quiz_result(self, result: Dict[str, Any]) -> str:
        """Formata resultado do quiz para exibição"""
        output = f"📊 **Resultado do Quiz**\n\n"
        output += f"Score: **{result['score']:.0f}%** ({result['correct']}/{result['total']} corretas)\n"
        output += f"Pontos: {result['points']}/{result['max_points']}\n\n"

        if result['passed']:
            output += f"✅ **APROVADO!**\n"
            output += f"🏆 Badge conquistado: **{result['badge']}**\n"
            output += f"💰 Desconto: {int(result['benefits']['discount'] * 100)}%\n"
            output += f"🎯 Benefícios desbloqueados:\n"
            for perk in result['benefits']['special_perks']:
                output += f"  • {perk}\n"
        else:
            output += f"❌ **Não aprovado**\n"
            output += f"Você precisa de 80% ou mais para desbloquear benefícios.\n"
            output += f"Tente novamente com `quiz start`\n"

        # Mostrar respostas incorretas
        incorrect = [d for d in result['details'] if not d['correct']]
        if incorrect:
            output += f"\n📚 **Revisar:**\n"
            for detail in incorrect[:3]:  # Mostrar até 3 erros
                output += f"Q{detail['question_id']}: {detail['explanation']}\n"

        return output


# Exemplo de uso
if __name__ == "__main__":
    import asyncio

    async def test_quiz():
        integration = QuizChatIntegration()

        print("=" * 60)
        print("🎮 Teste do Sistema de Quiz FNS")
        print("=" * 60)

        # Simular comandos
        user_id = "test_user"

        # Iniciar quiz
        response = await integration.handle_quiz_command(user_id, "quiz start")
        print(response)

        # Submeter respostas (simulando respostas corretas)
        response = await integration.handle_quiz_command(user_id, "quiz submit C,B,C,C,B")
        print(response)

        # Verificar status
        response = await integration.handle_quiz_command(user_id, "quiz status")
        print(response)

    asyncio.run(test_quiz())