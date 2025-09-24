"""Neo4j memory service for Flow agents"""

from neo4j import AsyncGraphDatabase
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class Neo4jMemory:
    """Serviço de memória persistente usando Neo4j"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o serviço Neo4j

        Args:
            config: Configuração do Neo4j (uri, username, password)
        """
        self.uri = config.get("uri", "bolt://localhost:7687")
        self.username = config.get("username", "neo4j")
        self.password = config.get("password", "password")
        self.driver = None

    async def connect(self):
        """Conecta ao Neo4j"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Verificar conexão
            async with self.driver.session() as session:
                result = await session.run("RETURN 1")
                await result.single()
            print("✅ Neo4j conectado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao conectar Neo4j: {e}")
            raise

    async def disconnect(self):
        """Desconecta do Neo4j"""
        if self.driver:
            await self.driver.close()
            print("✅ Neo4j desconectado")

    async def create_memory(self, data: Dict[str, Any]) -> str:
        """
        Cria uma nova memória no grafo

        Args:
            data: Dados da memória

        Returns:
            ID da memória criada
        """
        async with self.driver.session() as session:
            query = """
            CREATE (m:Learning {
                id: randomUUID(),
                type: $type,
                data: $data,
                timestamp: datetime(),
                created_at: $created_at
            })
            RETURN m.id as id
            """

            result = await session.run(
                query,
                type=data.get("type", "general"),
                data=json.dumps(data),
                created_at=datetime.now().isoformat()
            )

            record = await result.single()
            return record["id"] if record else None

    async def find_memories(self, query: str = None, type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca memórias no grafo

        Args:
            query: Texto para buscar
            type: Tipo de memória
            limit: Limite de resultados

        Returns:
            Lista de memórias encontradas
        """
        async with self.driver.session() as session:
            cypher_query = "MATCH (m:Learning) WHERE 1=1"
            params = {"limit": limit}

            if type:
                cypher_query += " AND m.type = $type"
                params["type"] = type

            if query:
                cypher_query += " AND (m.data CONTAINS $query OR m.type CONTAINS $query)"
                params["query"] = query

            cypher_query += " RETURN m ORDER BY m.timestamp DESC LIMIT $limit"

            result = await session.run(cypher_query, **params)
            memories = []

            async for record in result:
                node = record["m"]
                memory = dict(node)
                if "data" in memory:
                    try:
                        memory["data"] = json.loads(memory["data"])
                    except:
                        pass
                memories.append(memory)

            return memories

    async def create_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any] = None):
        """
        Cria relacionamento entre memórias

        Args:
            from_id: ID da memória origem
            to_id: ID da memória destino
            rel_type: Tipo do relacionamento
            properties: Propriedades do relacionamento
        """
        async with self.driver.session() as session:
            query = """
            MATCH (from:Learning {id: $from_id})
            MATCH (to:Learning {id: $to_id})
            CREATE (from)-[r:RELATES_TO {type: $rel_type}]->(to)
            SET r += $properties
            RETURN r
            """

            await session.run(
                query,
                from_id=from_id,
                to_id=to_id,
                rel_type=rel_type,
                properties=properties or {}
            )

    async def get_agent_context(self, agent_name: str) -> Dict[str, Any]:
        """
        Obtém contexto completo do agente

        Args:
            agent_name: Nome do agente

        Returns:
            Contexto do agente com memórias e relacionamentos
        """
        async with self.driver.session() as session:
            # Buscar memórias do agente
            query = """
            MATCH (m:Learning)
            WHERE m.data CONTAINS $agent_name
            OPTIONAL MATCH (m)-[r]-(related:Learning)
            RETURN
                m as memory,
                collect(DISTINCT {
                    node: related,
                    relationship: type(r)
                }) as connections
            ORDER BY m.timestamp DESC
            LIMIT 50
            """

            result = await session.run(query, agent_name=agent_name)

            context = {
                "agent": agent_name,
                "memories": [],
                "connections": [],
                "stats": {}
            }

            async for record in result:
                memory = dict(record["memory"])
                if "data" in memory:
                    try:
                        memory["data"] = json.loads(memory["data"])
                    except:
                        pass

                context["memories"].append({
                    "memory": memory,
                    "connections": [
                        {
                            "type": conn["relationship"],
                            "node": dict(conn["node"]) if conn["node"] else None
                        }
                        for conn in record["connections"] if conn["node"]
                    ]
                })

            # Estatísticas
            context["stats"] = {
                "total_memories": len(context["memories"]),
                "total_connections": sum(len(m["connections"]) for m in context["memories"])
            }

            return context

    async def learn_from_action(self, action: str, result: Any, success: bool = True):
        """
        Aprende com o resultado de uma ação

        Args:
            action: Ação executada
            result: Resultado obtido
            success: Se foi bem-sucedida
        """
        learning = {
            "type": "action_learning",
            "action": action,
            "result": str(result),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }

        memory_id = await self.create_memory(learning)

        # Buscar memórias similares para criar relacionamentos
        similar = await self.find_memories(query=action, limit=5)
        for mem in similar:
            if mem.get("id") and mem["id"] != memory_id:
                await self.create_relationship(
                    memory_id,
                    mem["id"],
                    "SIMILAR_ACTION",
                    {"similarity": "action_based"}
                )

    async def get_suggestions(self, context: str) -> List[str]:
        """
        Obtém sugestões baseadas no contexto

        Args:
            context: Contexto atual

        Returns:
            Lista de sugestões
        """
        # Buscar memórias relevantes
        memories = await self.find_memories(query=context, limit=10)

        suggestions = []
        for memory in memories:
            if memory.get("type") == "action_learning":
                data = memory.get("data", {})
                if isinstance(data, dict) and data.get("success"):
                    action = data.get("action", "")
                    if action and action not in suggestions:
                        suggestions.append(action)

        return suggestions[:5]  # Retornar top 5 sugestões