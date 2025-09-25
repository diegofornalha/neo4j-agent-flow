"""
Neo4j Integration for Flow Name Service (FNS)
Armazena registros de nomes, badges, transferências e relacionamentos
"""

from neo4j import GraphDatabase
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class FNSNeo4jIntegration:
    """
    Integração do FNS com Neo4j para persistência de dados
    Permite que participantes do bootcamp consultem e interajam com os dados
    """

    def __init__(self):
        # Configuração do Neo4j
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

        # Criar índices e constraints
        self._setup_database()

    def _setup_database(self):
        """Configura índices e constraints no banco"""
        with self.driver.session() as session:
            # Constraint para nome único
            session.run("""
                CREATE CONSTRAINT unique_find_name IF NOT EXISTS
                FOR (n:FindName) REQUIRE n.name IS UNIQUE
            """)

            # Índice para endereços
            session.run("""
                CREATE INDEX find_owner_index IF NOT EXISTS
                FOR (n:FindName) ON (n.owner)
            """)

            # Índice para participantes
            session.run("""
                CREATE INDEX participant_address IF NOT EXISTS
                FOR (p:Participant) ON (p.address)
            """)

    # ========== REGISTRO DE NOMES ==========

    def save_name_registration(
        self,
        name: str,
        owner_address: str,
        buyer_address: str,
        tier: str,
        fee: float,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Salva um registro de nome .find no Neo4j

        Args:
            name: Nome registrado (sem .find)
            owner_address: Endereço do proprietário
            buyer_address: Quem pagou pelo nome
            tier: Tier do nome (exclusive, premium, standard)
            fee: Taxa paga em FLOW
            transaction_id: ID da transação na blockchain

        Returns:
            Dados do registro salvo
        """
        with self.driver.session() as session:
            result = session.run("""
                // Criar ou atualizar participante proprietário
                MERGE (owner:Participant {address: $owner_address})
                ON CREATE SET
                    owner.created_at = datetime(),
                    owner.first_name_registered = datetime()

                // Criar ou atualizar participante comprador (se diferente)
                MERGE (buyer:Participant {address: $buyer_address})

                // Criar nome .find
                CREATE (name:FindName {
                    name: $name,
                    full_name: $name + '.find',
                    owner: $owner_address,
                    tier: $tier,
                    fee: $fee,
                    registered_at: datetime(),
                    transaction_id: $transaction_id,
                    status: 'active'
                })

                // Criar relacionamentos
                CREATE (owner)-[:OWNS]->(name)
                CREATE (buyer)-[:PURCHASED]->(name)

                // Adicionar à memória de aprendizado
                CREATE (learning:Learning {
                    type: 'fns_registration',
                    name: $name,
                    owner: $owner_address,
                    buyer: $buyer_address,
                    tier: $tier,
                    fee: $fee,
                    timestamp: datetime(),
                    context: 'Flow Bootcamp 2024'
                })

                CREATE (learning)-[:REFERS_TO]->(name)
                CREATE (learning)-[:INVOLVES]->(owner)

                RETURN name, owner.address as owner_address
            """,
                name=name,
                owner_address=owner_address,
                buyer_address=buyer_address,
                tier=tier,
                fee=fee,
                transaction_id=transaction_id
            )

            record = result.single()
            if record:
                return {
                    "success": True,
                    "name": name,
                    "owner": owner_address,
                    "message": f"Nome {name}.find registrado no Neo4j"
                }

            return {"success": False, "error": "Falha ao salvar no Neo4j"}

    # ========== QUIZ E BADGES ==========

    def save_quiz_result(
        self,
        participant_address: str,
        score: int,
        badge: Optional[str] = None,
        discount: float = 0.0,
        answers: Dict[int, int] = None
    ) -> Dict[str, Any]:
        """
        Salva resultado do quiz e badges conquistados

        Args:
            participant_address: Endereço do participante
            score: Pontuação obtida (0-100)
            badge: Badge conquistado (flow-expert, flow-master)
            discount: Desconto conquistado
            answers: Respostas do quiz

        Returns:
            Dados do resultado salvo
        """
        with self.driver.session() as session:
            result = session.run("""
                // Criar ou atualizar participante
                MERGE (p:Participant {address: $address})

                // Criar resultado do quiz
                CREATE (quiz:QuizResult {
                    participant: $address,
                    score: $score,
                    badge: $badge,
                    discount: $discount,
                    completed_at: datetime(),
                    answers: $answers
                })

                // Criar relacionamento
                CREATE (p)-[:COMPLETED]->(quiz)

                // Se conquistou badge, criar nó de badge
                FOREACH (b IN CASE WHEN $badge IS NOT NULL THEN [1] ELSE [] END |
                    MERGE (badge:Badge {name: $badge})
                    CREATE (p)-[:EARNED]->(badge)
                    CREATE (quiz)-[:GRANTED]->(badge)
                )

                // Adicionar à memória de aprendizado
                CREATE (learning:Learning {
                    type: 'quiz_completion',
                    participant: $address,
                    score: $score,
                    badge: $badge,
                    timestamp: datetime(),
                    context: 'FNS Quiz - Flow Bootcamp 2024'
                })

                CREATE (learning)-[:INVOLVES]->(p)
                CREATE (learning)-[:REFERS_TO]->(quiz)

                RETURN quiz, p.address as participant
            """,
                address=participant_address,
                score=score,
                badge=badge,
                discount=discount,
                answers=str(answers) if answers else None
            )

            record = result.single()
            if record:
                return {
                    "success": True,
                    "participant": participant_address,
                    "score": score,
                    "badge": badge,
                    "message": f"Quiz salvo: {score}% - Badge: {badge or 'Nenhum'}"
                }

            return {"success": False, "error": "Falha ao salvar quiz"}

    # ========== TRANSFERÊNCIAS ==========

    def save_name_transfer(
        self,
        name: str,
        from_address: str,
        to_address: str,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra transferência de nome .find entre participantes

        Args:
            name: Nome transferido
            from_address: Endereço anterior
            to_address: Novo endereço
            transaction_id: ID da transação

        Returns:
            Dados da transferência
        """
        with self.driver.session() as session:
            result = session.run("""
                // Encontrar o nome
                MATCH (name:FindName {name: $name})
                MATCH (from:Participant {address: $from_address})
                MATCH (from)-[old_owns:OWNS]->(name)

                // Criar novo proprietário
                MERGE (to:Participant {address: $to_address})

                // Deletar ownership antigo
                DELETE old_owns

                // Criar novo ownership
                CREATE (to)-[:OWNS]->(name)

                // Registrar transferência
                CREATE (transfer:Transfer {
                    name: $name,
                    from_address: $from_address,
                    to_address: $to_address,
                    transferred_at: datetime(),
                    transaction_id: $transaction_id
                })

                // Criar relacionamentos da transferência
                CREATE (from)-[:TRANSFERRED]->(transfer)
                CREATE (transfer)-[:TO]->(to)
                CREATE (transfer)-[:OF]->(name)

                // Atualizar proprietário do nome
                SET name.owner = $to_address,
                    name.last_transfer = datetime()

                // Adicionar à memória
                CREATE (learning:Learning {
                    type: 'name_transfer',
                    name: $name,
                    from: $from_address,
                    to: $to_address,
                    timestamp: datetime(),
                    context: 'NFT Transfer - Flow Bootcamp 2024'
                })

                CREATE (learning)-[:REFERS_TO]->(transfer)

                RETURN transfer, name.full_name as full_name
            """,
                name=name,
                from_address=from_address,
                to_address=to_address,
                transaction_id=transaction_id
            )

            record = result.single()
            if record:
                return {
                    "success": True,
                    "name": name,
                    "from": from_address,
                    "to": to_address,
                    "message": f"Transferência de {name}.find registrada"
                }

            return {"success": False, "error": "Falha ao registrar transferência"}

    # ========== CONSULTAS PARA O BOOTCAMP ==========

    def get_participant_names(self, address: str) -> List[Dict[str, Any]]:
        """
        Retorna todos os nomes que um participante possui

        Args:
            address: Endereço do participante

        Returns:
            Lista de nomes possuídos
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Participant {address: $address})-[:OWNS]->(name:FindName)
                RETURN name.name as name,
                       name.full_name as full_name,
                       name.tier as tier,
                       name.registered_at as registered_at
                ORDER BY name.registered_at DESC
            """, address=address)

            names = []
            for record in result:
                names.append({
                    "name": record["name"],
                    "full_name": record["full_name"],
                    "tier": record["tier"],
                    "registered_at": str(record["registered_at"])
                })

            return names

    def get_participant_badges(self, address: str) -> List[str]:
        """
        Retorna badges conquistados por um participante

        Args:
            address: Endereço do participante

        Returns:
            Lista de badges
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Participant {address: $address})-[:EARNED]->(badge:Badge)
                RETURN badge.name as badge_name
            """, address=address)

            return [record["badge_name"] for record in result]

    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do evento/bootcamp

        Returns:
            Estatísticas gerais
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Participant)
                WITH count(p) as total_participants

                MATCH (n:FindName)
                WITH total_participants, count(n) as total_names

                MATCH (q:QuizResult)
                WITH total_participants, total_names, count(q) as total_quizzes

                MATCH (b:Badge)
                WITH total_participants, total_names, total_quizzes, count(b) as total_badges

                MATCH (t:Transfer)
                WITH total_participants, total_names, total_quizzes, total_badges, count(t) as total_transfers

                RETURN total_participants, total_names, total_quizzes, total_badges, total_transfers
            """)

            record = result.single()
            if record:
                return {
                    "participants": record["total_participants"],
                    "names_registered": record["total_names"],
                    "quizzes_completed": record["total_quizzes"],
                    "badges_earned": record["total_badges"],
                    "transfers": record["total_transfers"]
                }

            return {
                "participants": 0,
                "names_registered": 0,
                "quizzes_completed": 0,
                "badges_earned": 0,
                "transfers": 0
            }

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna leaderboard do quiz

        Args:
            limit: Número de resultados

        Returns:
            Top participantes no quiz
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Participant)-[:COMPLETED]->(q:QuizResult)
                RETURN p.address as address,
                       max(q.score) as best_score,
                       collect(DISTINCT q.badge)[0] as badge
                ORDER BY best_score DESC
                LIMIT $limit
            """, limit=limit)

            leaderboard = []
            for i, record in enumerate(result, 1):
                leaderboard.append({
                    "position": i,
                    "address": record["address"],
                    "score": record["best_score"],
                    "badge": record["badge"]
                })

            return leaderboard

    def search_names_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Busca nomes por padrão

        Args:
            pattern: Padrão de busca

        Returns:
            Nomes encontrados
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:FindName)
                WHERE n.name CONTAINS $pattern
                RETURN n.name as name,
                       n.full_name as full_name,
                       n.owner as owner,
                       n.tier as tier
                ORDER BY n.name
                LIMIT 20
            """, pattern=pattern.lower())

            names = []
            for record in result:
                names.append({
                    "name": record["name"],
                    "full_name": record["full_name"],
                    "owner": record["owner"],
                    "tier": record["tier"]
                })

            return names

    def close(self):
        """Fecha conexão com Neo4j"""
        self.driver.close()


# ========== Exemplo de Uso ==========

if __name__ == "__main__":
    # Inicializar integração
    neo4j_fns = FNSNeo4jIntegration()

    print("=" * 60)
    print("🔷 Neo4j Integration for FNS - Teste")
    print("=" * 60)

    # Exemplo 1: Salvar registro de nome
    print("\n1. Salvando registro de nome:")
    result = neo4j_fns.save_name_registration(
        name="alice",
        owner_address="0x123abc",
        buyer_address="0x25f823e2a115b2dc",
        tier="standard",
        fee=5.0
    )
    print(f"   {result['message']}")

    # Exemplo 2: Salvar resultado de quiz
    print("\n2. Salvando resultado de quiz:")
    quiz_result = neo4j_fns.save_quiz_result(
        participant_address="0x123abc",
        score=85,
        badge="flow-expert",
        discount=0.20
    )
    print(f"   {quiz_result['message']}")

    # Exemplo 3: Buscar nomes de participante
    print("\n3. Nomes do participante 0x123abc:")
    names = neo4j_fns.get_participant_names("0x123abc")
    for name in names:
        print(f"   - {name['full_name']} ({name['tier']})")

    # Exemplo 4: Estatísticas do evento
    print("\n4. Estatísticas do Bootcamp:")
    stats = neo4j_fns.get_event_statistics()
    print(f"   Participantes: {stats['participants']}")
    print(f"   Nomes registrados: {stats['names_registered']}")
    print(f"   Quizzes completados: {stats['quizzes_completed']}")

    neo4j_fns.close()
    print("\n✅ Teste concluído!")