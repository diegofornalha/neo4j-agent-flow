"""
Natural Language .find Manager
Processa comandos em linguagem natural para gerenciar nomes .find
Sem comandos com / - apenas conversação natural!
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re
import json

class NaturalLanguageFindManager:
    """
    Gerenciador de nomes .find usando apenas linguagem natural
    """

    def __init__(self):
        self.staff_account = "0x01cf0e2f2f715450"
        self.registered_participants = []
        self.event_id = "bootcamp2024"

        # Padrões de linguagem natural
        self.patterns = {
            'register': [
                r'registr[ae]r?\s+(?:o\s+)?(?:nome\s+)?(\w+)',
                r'criar?\s+(?:nome\s+)?(\w+)\.find',
                r'(?:quero|preciso)\s+(?:o\s+)?(?:nome\s+)?(\w+)\.find',
                r'(?:cadastr[ae]r?|inscrever?)\s+(\w+)\s+(?:no|para)?\s*(?:quiz|evento)?',
                r'(?:fazer?|realizar?)\s+check-?in\s+(?:de\s+)?(\w+)',
                r'participante\s+(\w+)\s+chegou',
                r'(\w+)\s+(?:está|esta)\s+(?:aqui|presente)',
                r'adicionar?\s+(\w+)\s+(?:na|à)?\s*lista'
            ],

            'batch_register': [
                r'registr[ae]r?\s+(?:os\s+)?(?:participantes?\s+)?([^\.]+)',
                r'(?:cadastr[ae]r?|inscrever?)\s+(?:todos?\s+)?:?\s*([^\.]+)',
                r'check-?in\s+(?:em\s+)?(?:massa|lote|grupo)\s*:?\s*([^\.]+)',
                r'chegaram\s*:?\s*([^\.]+)',
                r'lista\s+de\s+presença\s*:?\s*([^\.]+)'
            ],

            'check_availability': [
                r'(\w+)\.find\s+(?:está|esta)\s+dispon[ií]vel',
                r'(?:posso|consigo)\s+(?:ter|pegar|comprar)\s+(?:o\s+)?(?:nome\s+)?(\w+)',
                r'(?:verificar?|checar?)\s+(?:se\s+)?(\w+)\.find\s+(?:existe|está\s+livre)',
                r'(\w+)\s+(?:já|ja)\s+(?:foi\s+)?(?:registrado|existe)',
                r'tem\s+(?:o\s+)?(?:nome\s+)?(\w+)\.find'
            ],

            'resolve': [
                r'(?:qual|quais)\s+(?:o\s+)?(?:endereço|endereco)\s+de\s+(\w+)\.find',
                r'(\w+)\.find\s+(?:aponta|resolve)\s+para',
                r'(?:buscar?|procurar?)\s+(?:endereço|endereco)\s+de\s+(\w+)',
                r'(?:quem|qual)\s+(?:é|e)\s+(\w+)\.find'
            ],

            'list': [
                r'(?:listar?|mostrar?)\s+(?:os\s+)?(?:últimos|ultimos|todos)',
                r'quem\s+(?:já|ja)\s+(?:fez\s+)?check-?in',
                r'(?:quantos?|quantas?)\s+(?:pessoas?|participantes?)\s+(?:já|ja)',
                r'(?:ver|mostrar?)\s+(?:a\s+)?lista\s+de\s+presença',
                r'quem\s+(?:está|esta)\s+(?:registrado|inscrito|presente)'
            ],

            'info': [
                r'(?:status|info|informações|informacoes)\s+do\s+(?:sistema|evento)',
                r'como\s+(?:está|esta)\s+o\s+(?:evento|quiz|bootcamp)',
                r'(?:quantos?|quantas?)\s+(?:pessoas?|participantes?)\s+(?:no\s+)?total',
                r'(?:estatísticas|estatisticas|números|numeros)\s+do\s+evento'
            ],

            'buy': [
                r'(?:comprar?|adquirir?)\s+(?:o\s+)?(?:nome\s+)?(\w+)\.find',
                r'(?:quero|desejo|preciso)\s+(?:comprar?)\s+(\w+)\.find',
                r'(?:quanto|preço|preco|valor)\s+(?:de\s+)?(\w+)\.find'
            ]
        }

    def understand_intent(self, message: str) -> Dict[str, Any]:
        """
        Entende a intenção do usuário através de linguagem natural
        """
        message_lower = message.lower().strip()

        # Verifica cada tipo de intenção
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    return self._process_intent(intent, match, message_lower)

        # Se não encontrou padrão específico, tenta entender contexto
        return self._fallback_understanding(message_lower)

    def _process_intent(self, intent: str, match: re.Match, message: str) -> Dict[str, Any]:
        """
        Processa a intenção identificada
        """
        if intent == 'register':
            name = match.group(1)
            return self._register_single(name)

        elif intent == 'batch_register':
            names_str = match.group(1)
            names = self._extract_names(names_str)
            return self._register_batch(names)

        elif intent == 'check_availability':
            name = match.group(1)
            return self._check_availability(name)

        elif intent == 'resolve':
            name = match.group(1)
            return self._resolve_name(name)

        elif intent == 'list':
            return self._list_participants()

        elif intent == 'info':
            return self._get_info()

        elif intent == 'buy':
            name = match.group(1)
            return self._prepare_purchase(name)

        return {"success": False, "message": "Não entendi completamente. Pode reformular?"}

    def _register_single(self, name: str) -> Dict[str, Any]:
        """
        Registra um único participante
        """
        # Gera endereço temporário se não fornecido
        address = f"0x{hash(name + str(datetime.now())):#016x}"[2:18]
        unique_name = f"{name}-{self.event_id}-{len(self.registered_participants)}"

        self.registered_participants.append({
            "name": unique_name,
            "original": name,
            "address": address,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "action": "register",
            "name": f"{unique_name}.find",
            "participant": name,
            "message": f"✅ Legal! Registrei {name} como **{unique_name}.find**! Agora {name} pode participar do Quiz Race!",
            "total": len(self.registered_participants)
        }

    def _register_batch(self, names: List[str]) -> Dict[str, Any]:
        """
        Registra múltiplos participantes
        """
        registered = []
        for name in names:
            if name:  # Ignora strings vazias
                address = f"0x{hash(name + str(datetime.now())):#016x}"[2:18]
                unique_name = f"{name}-{self.event_id}-{len(self.registered_participants)}"

                self.registered_participants.append({
                    "name": unique_name,
                    "original": name,
                    "address": address,
                    "timestamp": datetime.now().isoformat()
                })
                registered.append(unique_name)

        return {
            "success": True,
            "action": "batch_register",
            "count": len(registered),
            "names": [f"{n}.find" for n in registered],
            "message": f"🎉 Massa! Registrei {len(registered)} participantes:\n" +
                      "\n".join([f"• {name}" for name in registered[:5]]) +
                      (f"\n... e mais {len(registered)-5}" if len(registered) > 5 else ""),
            "total": len(self.registered_participants)
        }

    def _check_availability(self, name: str) -> Dict[str, Any]:
        """
        Verifica disponibilidade de um nome
        """
        # Simula verificação
        is_taken = any(p['original'].lower() == name.lower()
                      for p in self.registered_participants)

        if is_taken:
            return {
                "success": True,
                "action": "check",
                "available": False,
                "name": f"{name}.find",
                "message": f"❌ Ops! {name}.find já foi registrado. Que tal tentar {name}2024.find ou {name}flow.find?",
                "suggestions": [f"{name}2024", f"{name}flow", f"super{name}"]
            }

        return {
            "success": True,
            "action": "check",
            "available": True,
            "name": f"{name}.find",
            "message": f"🎊 Boa notícia! {name}.find está disponível! Quer que eu registre para você?",
            "price": "GRÁTIS no bootcamp!"
        }

    def _resolve_name(self, name: str) -> Dict[str, Any]:
        """
        Resolve nome para endereço
        """
        for participant in self.registered_participants:
            if participant['original'].lower() == name.lower():
                return {
                    "success": True,
                    "action": "resolve",
                    "name": f"{participant['name']}.find",
                    "address": participant['address'],
                    "message": f"📍 Encontrei! {participant['name']}.find pertence ao endereço:\n`{participant['address']}`"
                }

        return {
            "success": True,
            "action": "resolve",
            "name": f"{name}.find",
            "found": False,
            "message": f"🔍 Hmm, não encontrei {name}.find registrado ainda. Quer registrar agora?"
        }

    def _list_participants(self) -> Dict[str, Any]:
        """
        Lista participantes registrados
        """
        if not self.registered_participants:
            return {
                "success": True,
                "action": "list",
                "count": 0,
                "message": "📋 Ainda não temos ninguém registrado. Vamos começar? Diga algo como 'registrar João'!"
            }

        recent = self.registered_participants[-10:]
        names_list = "\n".join([f"• {p['original']} → {p['name']}.find"
                                for p in recent])

        return {
            "success": True,
            "action": "list",
            "count": len(self.registered_participants),
            "recent": recent,
            "message": f"📋 **{len(self.registered_participants)} participantes registrados!**\n\nÚltimos registros:\n{names_list}",
            "ready_for_quiz": len(self.registered_participants) >= 5
        }

    def _get_info(self) -> Dict[str, Any]:
        """
        Informações do sistema
        """
        status_emoji = "🟢" if len(self.registered_participants) > 0 else "🟡"

        return {
            "success": True,
            "action": "info",
            "event": self.event_id,
            "total_registered": len(self.registered_participants),
            "message": f"""
{status_emoji} **Status do Bootcamp Flow 2024**

📊 **Números:**
• Participantes registrados: {len(self.registered_participants)}
• Nomes .find criados: {len(self.registered_participants)}
• Quiz Race: {'PRONTO! 🎮' if len(self.registered_participants) >= 5 else f'Precisamos de mais {5 - len(self.registered_participants)} pessoas'}

💰 **Prêmios:**
• 1º lugar: 300 FLOW
• 2º lugar: 250 FLOW
• 3º lugar: 200 FLOW
• 4º lugar: 150 FLOW
• 5º lugar: 100 FLOW

🎯 **Como participar:**
Diga "registrar [nome]" para adicionar alguém!
            """,
            "ready": len(self.registered_participants) >= 5
        }

    def _prepare_purchase(self, name: str) -> Dict[str, Any]:
        """
        Prepara compra de nome .find
        """
        return {
            "success": True,
            "action": "buy",
            "name": f"{name}.find",
            "message": f"""
💳 **Quer comprar {name}.find?**

Durante o bootcamp é GRÁTIS! 🎉

Fora do evento:
• Preço normal: 5.0 FLOW
• Desconto quiz: 1.0 FLOW

Quer que eu registre {name} gratuitamente agora?
            """,
            "special_offer": "GRÁTIS no bootcamp!"
        }

    def _extract_names(self, text: str) -> List[str]:
        """
        Extrai nomes de um texto
        """
        # Remove pontuação e separa por vírgula, 'e', espaços
        text = re.sub(r'[^\w\s,]', '', text)

        # Tenta diferentes separadores
        names = []

        # Por vírgula
        if ',' in text:
            names = [n.strip() for n in text.split(',')]
        # Por 'e'
        elif ' e ' in text:
            names = [n.strip() for n in text.split(' e ')]
        # Por espaços (assumindo cada palavra é um nome)
        else:
            names = text.split()

        # Remove palavras comuns que não são nomes
        stopwords = ['o', 'a', 'de', 'da', 'do', 'para', 'com', 'os', 'as']
        names = [n for n in names if n.lower() not in stopwords and len(n) > 1]

        return names

    def _fallback_understanding(self, message: str) -> Dict[str, Any]:
        """
        Resposta quando não entende o comando
        """
        # Tenta identificar contexto pela presença de palavras-chave
        if '.find' in message:
            return {
                "success": False,
                "message": """
🤔 Vi que você mencionou .find! Posso ajudar com:

• **Registrar alguém:** "registrar Maria"
• **Verificar nome:** "joão.find está disponível?"
• **Ver lista:** "quem já fez check-in?"
• **Informações:** "como está o evento?"

O que você gostaria de fazer?
                """
            }

        if any(word in message for word in ['quiz', 'evento', 'bootcamp']):
            return self._get_info()

        return {
            "success": False,
            "message": """
👋 Oi! Sou o assistente do Quiz Race! Como posso ajudar?

Alguns exemplos do que posso fazer:
• "Registrar João para o quiz"
• "Maria e Pedro chegaram"
• "Verificar se alice.find existe"
• "Mostrar quem já está presente"
• "Status do evento"

É só falar naturalmente comigo! 😊
            """
        }

    def chat(self, message: str, sender: str = None) -> str:
        """
        Interface principal de chat
        """
        result = self.understand_intent(message)
        return result.get('message', 'Desculpe, não entendi. Pode repetir?')

# ===================================
# EXEMPLOS DE USO
# ===================================

def test_natural_language():
    """
    Testa processamento de linguagem natural
    """
    manager = NaturalLanguageFindManager()

    # Exemplos de mensagens naturais
    test_messages = [
        "oi, como funciona isso?",
        "quero registrar o João",
        "Maria chegou para o evento",
        "fazer check-in de Pedro",
        "alice.find está disponível?",
        "cadastrar Ana, Bruno e Carlos",
        "chegaram: Daniel, Eduardo, Fernanda",
        "quem já fez check-in?",
        "quantas pessoas temos?",
        "status do sistema",
        "qual o endereço de João.find?",
        "quero comprar meu nome lucas.find"
    ]

    print("=" * 60)
    print("🤖 TESTE DE LINGUAGEM NATURAL")
    print("=" * 60)

    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = manager.chat(msg)
        print(f"🤖 Bot: {response[:200]}...")  # Primeiros 200 chars

if __name__ == "__main__":
    test_natural_language()