"""
Quiz Race + .find Name Service Integration
Sistema híbrido: Nome .find funciona como NFT de acesso ao Quiz
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

class QuizFindIntegration:
    """
    Integração completa entre Quiz Race e .find Name Service
    """

    def __init__(self, network: str = "testnet"):
        self.network = network
        self.contracts = {
            "FIND": "0x35717efbbce11c74" if network == "testnet" else "0x097bafa4e0b48eef",
            "QuizRace": "0x01cf0e2f2f715450",  # Nosso contrato
            "FlowToken": "0x7e60df042a9c0868",
            "FungibleToken": "0x9a0766d93b6608b7"
        }

    # ===================================
    # CONTRATO HÍBRIDO QUIZ + .FIND
    # ===================================

    def deploy_quiz_find_contract(self) -> str:
        """
        Contrato que usa .find names como tickets de acesso
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import FlowToken from {self.contracts["FlowToken"]}
        import FungibleToken from {self.contracts["FungibleToken"]}

        pub contract QuizRaceFind {{

            // Eventos
            pub event QuizCreated(id: UInt64, prize: UFix64, requiredNamePattern: String?)
            pub event ParticipantRegistered(quiz: UInt64, name: String, address: Address)
            pub event QuizCompleted(quiz: UInt64, winners: [String])
            pub event PrizePaid(winner: String, amount: UFix64)
            pub event NameNotEligible(address: Address, reason: String)

            // Estado do Quiz
            pub struct Quiz {{
                pub let id: UInt64
                pub let createdAt: UFix64
                pub let prizePool: UFix64
                pub let questions: [String]
                pub let correctAnswers: [String]
                pub var participants: {{Address: String}}  // address -> .find name
                pub var winners: [String]
                pub var isActive: Bool
                pub let namePattern: String?  // ex: "bootcamp" para aceitar só *bootcamp*.find

                init(prize: UFix64, questions: [String], answers: [String], pattern: String?) {{
                    self.id = QuizRaceFind.nextQuizId
                    QuizRaceFind.nextQuizId = QuizRaceFind.nextQuizId + 1
                    self.createdAt = getCurrentBlock().timestamp
                    self.prizePool = prize
                    self.questions = questions
                    self.correctAnswers = answers
                    self.participants = {{}}
                    self.winners = []
                    self.isActive = true
                    self.namePattern = pattern
                }}

                pub fun canParticipate(_ address: Address): Bool {{
                    // Verifica se tem nome .find
                    if let name = FIND.reverseLookup(address) {{
                        // Se tem padrão específico
                        if let pattern = self.namePattern {{
                            return name.contains(pattern)
                        }}
                        // Qualquer nome .find serve
                        return true
                    }}
                    return false
                }}

                pub fun registerParticipant(_ address: Address) {{
                    pre {{
                        self.canParticipate(address): "Precisa de nome .find válido!"
                        self.participants[address] == nil: "Já registrado!"
                    }}

                    let name = FIND.reverseLookup(address)!
                    self.participants[address] = name
                    emit ParticipantRegistered(
                        quiz: self.id,
                        name: name,
                        address: address
                    )
                }}
            }}

            // Armazenamento
            pub var quizzes: {{UInt64: Quiz}}
            pub var nextQuizId: UInt64
            pub let prizeVault: @FlowToken.Vault

            // ===================================
            // CRIAR QUIZ PARA BOOTCAMP
            // ===================================

            pub fun createBootcampQuiz(
                prize: UFix64,
                questions: [String],
                answers: [String]
            ): UInt64 {{
                let quiz = Quiz(
                    prize: prize,
                    questions: questions,
                    answers: answers,
                    pattern: "bootcamp"  // Só aceita nomes com "bootcamp"
                )

                self.quizzes[quiz.id] = quiz

                emit QuizCreated(
                    id: quiz.id,
                    prize: prize,
                    requiredNamePattern: "bootcamp"
                )

                return quiz.id
            }}

            // ===================================
            // PARTICIPAR DO QUIZ
            // ===================================

            pub fun joinQuiz(quizId: UInt64, participant: AuthAccount) {{
                let quiz = self.quizzes[quizId]
                    ?? panic("Quiz não existe")

                let address = participant.address

                // Verifica elegibilidade via .find
                if !quiz.canParticipate(address) {{
                    let reason = quiz.namePattern != nil
                        ? "Nome precisa conter: ".concat(quiz.namePattern!)
                        : "Precisa ter um nome .find"

                    emit NameNotEligible(address: address, reason: reason)
                    panic(reason)
                }}

                quiz.registerParticipant(address)
            }}

            // ===================================
            // SUBMETER RESPOSTAS
            // ===================================

            pub fun submitAnswers(
                quizId: UInt64,
                answers: [String],
                participant: AuthAccount
            ): Bool {{
                let quiz = self.quizzes[quizId]
                    ?? panic("Quiz não existe")

                let address = participant.address

                // Verifica se está registrado
                let name = quiz.participants[address]
                    ?? panic("Não registrado no quiz")

                // Verifica respostas
                var correct = 0
                for i, answer in answers {{
                    if answer == quiz.correctAnswers[i] {{
                        correct = correct + 1
                    }}
                }}

                // Se acertou tudo e está entre os 5 primeiros
                if correct == quiz.correctAnswers.length && quiz.winners.length < 5 {{
                    quiz.winners.append(name)

                    // Calcula prêmio baseado na posição
                    let prizeAmount = self.calculatePrize(
                        position: quiz.winners.length,
                        totalPrize: quiz.prizePool
                    )

                    // Paga prêmio
                    self.payWinner(address: address, amount: prizeAmount)

                    // Se já tem 5 vencedores, encerra
                    if quiz.winners.length >= 5 {{
                        quiz.isActive = false
                        emit QuizCompleted(quiz: quizId, winners: quiz.winners)
                    }}

                    return true
                }}

                return false
            }}

            // ===================================
            // PAGAMENTO DE PRÊMIOS
            // ===================================

            access(self) fun calculatePrize(position: Int, totalPrize: UFix64): UFix64 {{
                // Distribuição: 30%, 25%, 20%, 15%, 10%
                switch position {{
                    case 1: return totalPrize * 0.30
                    case 2: return totalPrize * 0.25
                    case 3: return totalPrize * 0.20
                    case 4: return totalPrize * 0.15
                    case 5: return totalPrize * 0.10
                    default: return 0.0
                }}
            }}

            access(self) fun payWinner(address: Address, amount: UFix64) {{
                let recipient = getAccount(address)
                let receiverRef = recipient
                    .getCapability(/public/flowTokenReceiver)
                    .borrow<&{{FungibleToken.Receiver}}>()
                    ?? panic("Could not borrow receiver reference")

                let payment <- self.prizeVault.withdraw(amount: amount)
                receiverRef.deposit(from: <-payment)

                // Busca nome para o evento
                let name = FIND.reverseLookup(address) ?? "unknown"
                emit PrizePaid(winner: name, amount: amount)
            }}

            // ===================================
            // VIEWS & QUERIES
            // ===================================

            pub fun getQuizInfo(quizId: UInt64): Quiz? {{
                return self.quizzes[quizId]
            }}

            pub fun getActiveQuizzes(): [UInt64] {{
                let active: [UInt64] = []
                for id in self.quizzes.keys {{
                    if self.quizzes[id]!.isActive {{
                        active.append(id)
                    }}
                }}
                return active
            }}

            pub fun getParticipantName(quizId: UInt64, address: Address): String? {{
                if let quiz = self.quizzes[quizId] {{
                    return quiz.participants[address]
                }}
                return nil
            }}

            pub fun getLeaderboard(quizId: UInt64): [String] {{
                return self.quizzes[quizId]?.winners ?? []
            }}

            // ===================================
            // INICIALIZAÇÃO
            // ===================================

            init() {{
                self.quizzes = {{}}
                self.nextQuizId = 1
                self.prizeVault <- FlowToken.createEmptyVault() as! @FlowToken.Vault
            }}
        }}
        '''

    # ===================================
    # TRANSAÇÕES PARA PARTICIPANTES
    # ===================================

    def register_bootcamp_participant_transaction(self) -> str:
        """
        Registra participante do bootcamp com nome .find especial
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import QuizRaceFind from {self.contracts["QuizRace"]}

        transaction(participantName: String) {{
            prepare(signer: AuthAccount) {{
                // Cria nome especial do bootcamp
                let bootcampName = participantName
                    .concat("-bootcamp")
                    .concat(getCurrentBlock().height.toString())

                // Registra nome .find (seria grátis no evento presencial)
                FIND.registerFreeBootcampName(
                    name: bootcampName,
                    recipient: signer.address
                )

                log("Nome .find registrado: ".concat(bootcampName).concat(".find"))
            }}
        }}
        '''

    def join_quiz_with_find_name(self) -> str:
        """
        Entra no quiz usando nome .find
        """
        return f'''
        import QuizRaceFind from {self.contracts["QuizRace"]}
        import FIND from {self.contracts["FIND"]}

        transaction(quizId: UInt64) {{
            prepare(signer: AuthAccount) {{
                // Verifica se tem nome .find
                let myName = FIND.reverseLookup(signer.address)
                    ?? panic("Você precisa de um nome .find! Registre em find.xyz")

                // Entra no quiz
                QuizRaceFind.joinQuiz(quizId: quizId, participant: signer)

                log("Entrou no quiz como: ".concat(myName).concat(".find"))
            }}
        }}
        '''

    # ===================================
    # SCRIPTS DE CONSULTA
    # ===================================

    def check_eligibility_script(self) -> str:
        """
        Verifica se endereço pode participar
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import QuizRaceFind from {self.contracts["QuizRace"]}

        pub struct EligibilityResult {{
            pub let hasFind: Bool
            pub let findName: String?
            pub let isEligible: Bool
            pub let reason: String

            init(hasFind: Bool, name: String?, eligible: Bool, reason: String) {{
                self.hasFind = hasFind
                self.findName = name
                self.isEligible = eligible
                self.reason = reason
            }}
        }}

        pub fun main(address: Address, quizId: UInt64): EligibilityResult {{
            // Busca nome .find
            let name = FIND.reverseLookup(address)

            if name == nil {{
                return EligibilityResult(
                    hasFind: false,
                    name: nil,
                    eligible: false,
                    reason: "Precisa de um nome .find para participar"
                )
            }}

            // Verifica requisitos do quiz
            let quiz = QuizRaceFind.getQuizInfo(quizId: quizId)
                ?? panic("Quiz não existe")

            if let pattern = quiz.namePattern {{
                let eligible = name!.contains(pattern)
                return EligibilityResult(
                    hasFind: true,
                    name: name,
                    eligible: eligible,
                    reason: eligible
                        ? "Elegível para participar!"
                        : "Nome precisa conter: ".concat(pattern)
                )
            }}

            return EligibilityResult(
                hasFind: true,
                name: name,
                eligible: true,
                reason: "Elegível para participar!"
            )
        }}
        '''

    def get_quiz_participants_with_names(self) -> str:
        """
        Lista participantes com seus nomes .find
        """
        return f'''
        import QuizRaceFind from {self.contracts["QuizRace"]}

        pub struct Participant {{
            pub let address: Address
            pub let findName: String
            pub let displayName: String

            init(address: Address, name: String) {{
                self.address = address
                self.findName = name
                self.displayName = name.concat(".find")
            }}
        }}

        pub fun main(quizId: UInt64): [Participant] {{
            let quiz = QuizRaceFind.getQuizInfo(quizId: quizId)
                ?? panic("Quiz não existe")

            let participants: [Participant] = []

            for address in quiz.participants.keys {{
                let name = quiz.participants[address]!
                participants.append(Participant(
                    address: address,
                    name: name
                ))
            }}

            return participants
        }}
        '''

    # ===================================
    # DASHBOARD AO VIVO
    # ===================================

    def create_live_dashboard_data(self) -> Dict:
        """
        Dados para dashboard ao vivo do evento
        """
        return {
            "quiz_status": {
                "active": True,
                "quiz_id": 1,
                "prize_pool": "1000 FLOW",
                "required_name": "*.find ou *bootcamp*.find"
            },
            "participants": {
                "total": 73,
                "with_find_names": 68,
                "eligible": 65,
                "playing_now": 12
            },
            "leaderboard": [
                {"position": 1, "name": "alice-bootcamp2024.find", "time": "2:45", "prize": "300 FLOW"},
                {"position": 2, "name": "bob.find", "time": "3:12", "prize": "250 FLOW"},
                {"position": 3, "name": "carol-quiz.find", "time": "3:28", "prize": "200 FLOW"},
                {"position": 4, "name": "[VAGA]", "time": "-", "prize": "150 FLOW"},
                {"position": 5, "name": "[VAGA]", "time": "-", "prize": "100 FLOW"}
            ],
            "live_feed": [
                "🎯 maria.find acabou de entrar no quiz!",
                "🏆 alice-bootcamp2024.find completou em 2:45!",
                "📝 pedro.find está na questão 7/10",
                "✨ joao-bootcamp.find registrou seu nome!"
            ]
        }

    # ===================================
    # VANTAGENS DO SISTEMA HÍBRIDO
    # ===================================

    def get_benefits(self) -> Dict:
        """
        Benefícios de usar .find como ticket
        """
        return {
            "para_participantes": {
                "identidade": "Nome memorável ao invés de 0x...",
                "permanente": "Nome .find fica para sempre",
                "tradeable": "Pode vender o nome depois",
                "social": "Perfil .find com badges e NFTs",
                "networking": "Outros encontram você facilmente"
            },
            "para_organizadores": {
                "anti_bot": "Custo de registro impede spam",
                "identificação": "Nomes legíveis no leaderboard",
                "marketing": "Participantes promovem seus nomes",
                "comunidade": "Rede de ex-participantes identificável",
                "analytics": "Rastrear participações históricas"
            },
            "técnicas": {
                "onchain": "100% verificável na blockchain",
                "composable": "Integra com outros dApps Flow",
                "standard": "Usa infraestrutura .find existente",
                "scalable": "Suporta milhares de participantes"
            }
        }

# ===================================
# EXEMPLO DE USO COMPLETO
# ===================================

def example_bootcamp_quiz():
    """
    Exemplo: Quiz do Bootcamp com .find names
    """
    integration = QuizFindIntegration(network="testnet")

    print("=" * 60)
    print("🎮 QUIZ RACE + .FIND INTEGRATION")
    print("=" * 60)

    # 1. Deploy do contrato
    print("\n1️⃣ DEPLOY DO CONTRATO HÍBRIDO")
    contract = integration.deploy_quiz_find_contract()
    print("Contrato QuizRaceFind pronto!")

    # 2. Registrar participante
    print("\n2️⃣ REGISTRO DE PARTICIPANTE")
    register_tx = integration.register_bootcamp_participant_transaction()
    print("Participante registra nome: joao-bootcamp2024.find")

    # 3. Verificar elegibilidade
    print("\n3️⃣ VERIFICAÇÃO DE ELEGIBILIDADE")
    eligibility = integration.check_eligibility_script()
    print("Script verifica se pode participar")

    # 4. Entrar no quiz
    print("\n4️⃣ ENTRADA NO QUIZ")
    join_tx = integration.join_quiz_with_find_name()
    print("Participa usando nome .find como ticket")

    # 5. Dashboard ao vivo
    print("\n5️⃣ DASHBOARD AO VIVO")
    dashboard = integration.create_live_dashboard_data()
    print(json.dumps(dashboard["leaderboard"], indent=2))

    # 6. Benefícios
    print("\n6️⃣ BENEFÍCIOS DO SISTEMA")
    benefits = integration.get_benefits()
    for category, items in benefits.items():
        print(f"\n{category.upper()}:")
        for key, value in items.items():
            print(f"  • {key}: {value}")

if __name__ == "__main__":
    example_bootcamp_quiz()