#!/usr/bin/env python3
"""
💾 SALVAR APRENDIZADO SOBRE FLOW + CADENCE 1.0 NO NEO4J
"""

from neo4j import GraphDatabase
import os
from datetime import datetime

# Configuração Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

print("💾 SALVANDO APRENDIZADO NO NEO4J")
print("=" * 60)

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Criar nó principal do aprendizado
        result = session.run("""
            CREATE (l:Learning {
                title: 'Flow Blockchain + Cadence 1.0 + FIND Integration',
                date: datetime($date),
                category: 'blockchain',
                importance: 'critical',
                status: 'resolved'
            })
            RETURN id(l) as learning_id
        """, date=datetime.now().isoformat())

        learning_id = result.single()["learning_id"]
        print(f"✅ Nó de aprendizado criado: ID {learning_id}")

        # 2. Adicionar problemas encontrados
        problems = [
            {
                'type': 'wrong_address',
                'description': 'Usávamos endereço da mainnet (0x097bafa4e0b48eef) na testnet',
                'solution': 'Usar endereço correto da testnet: 0x35717efbbce11c74'
            },
            {
                'type': 'entitlement_blocked',
                'description': 'LeaseOwner entitlement não disponível para usuários',
                'solution': 'Aguardar proxy contract ou atualização do FIND'
            },
            {
                'type': 'cadence_1_syntax',
                'description': 'Sintaxe antiga não funciona no Cadence 1.0',
                'solution': 'Usar intersection types e entitlements corretos'
            }
        ]

        for problem in problems:
            session.run("""
                MATCH (l:Learning) WHERE id(l) = $learning_id
                CREATE (p:Problem {
                    type: $type,
                    description: $description,
                    solution: $solution
                })
                CREATE (l)-[:HAS_PROBLEM]->(p)
            """, learning_id=learning_id, **problem)

        print(f"✅ {len(problems)} problemas documentados")

        # 3. Adicionar conceitos aprendidos
        concepts = [
            {
                'name': 'Intersection Types',
                'syntax': '@{FungibleToken.Vault}',
                'purpose': 'Usar interfaces como tipos no Cadence 1.0'
            },
            {
                'name': 'Entitlements',
                'syntax': 'auth(FungibleToken.Withdraw)',
                'purpose': 'Sistema de permissões granulares no Cadence 1.0'
            },
            {
                'name': 'Storage Access',
                'syntax': 'signer.storage.borrow',
                'purpose': 'Acessar apenas próprio storage, nunca de outros'
            }
        ]

        for concept in concepts:
            session.run("""
                MATCH (l:Learning) WHERE id(l) = $learning_id
                CREATE (c:Concept {
                    name: $name,
                    syntax: $syntax,
                    purpose: $purpose
                })
                CREATE (l)-[:TEACHES]->(c)
            """, learning_id=learning_id, **concept)

        print(f"✅ {len(concepts)} conceitos salvos")

        # 4. Adicionar código de exemplo funcional
        session.run("""
            MATCH (l:Learning) WHERE id(l) = $learning_id
            CREATE (e:Example {
                type: 'working_transaction',
                description: 'Transação simples funcional no Cadence 1.0',
                code: $code
            })
            CREATE (l)-[:HAS_EXAMPLE]->(e)
        """,
        learning_id=learning_id,
        code="""
        transaction {
            prepare(signer: auth(Storage) &Account) {
                log("Transação funcionando no Cadence 1.0")
                log(signer.address)
            }
        }
        """)

        # 5. Adicionar status do FIND
        session.run("""
            MATCH (l:Learning) WHERE id(l) = $learning_id
            CREATE (s:Status {
                project: 'FIND',
                network: 'testnet',
                issue: 'Registro bloqueado por entitlements',
                workaround: 'Nenhum disponível atualmente',
                last_checked: datetime($date)
            })
            CREATE (l)-[:CURRENT_STATUS]->(s)
        """, learning_id=learning_id, date=datetime.now().isoformat())

        # 6. Adicionar credenciais funcionais
        session.run("""
            MATCH (l:Learning) WHERE id(l) = $learning_id
            CREATE (cred:Credentials {
                account: '0x36395f9dde50ea27',
                balance: '101000 FLOW',
                algorithm: 'ECDSA_secp256k1',
                status: 'working',
                tested: true
            })
            CREATE (l)-[:USES_CREDENTIALS]->(cred)
        """, learning_id=learning_id)

        print("✅ Credenciais documentadas")

        # 7. Criar resumo executivo
        session.run("""
            MATCH (l:Learning) WHERE id(l) = $learning_id
            SET l.summary = $summary
        """,
        learning_id=learning_id,
        summary="""
        Descobrimos que o registro de nomes .find está bloqueado na testnet devido ao sistema
        de entitlements do Cadence 1.0. O entitlement LeaseOwner é necessário mas não está
        disponível para usuários. Também identificamos uso de endereço incorreto (mainnet ao
        invés de testnet). Solução requer atualização do FIND ou criação de proxy contract.
        """)

        print("✅ Resumo executivo adicionado")

        # Verificar o que foi salvo
        result = session.run("""
            MATCH (l:Learning {title: 'Flow Blockchain + Cadence 1.0 + FIND Integration'})
            OPTIONAL MATCH (l)-[r]->(n)
            RETURN count(r) as relationships
        """)

        count = result.single()["relationships"]
        print(f"\n📊 Total de relacionamentos criados: {count}")

        print("\n🎉 APRENDIZADO SALVO COM SUCESSO NO NEO4J!")
        print("\nPara visualizar no Neo4j Browser:")
        print("MATCH (l:Learning {category: 'blockchain'})-[r]->(n)")
        print("RETURN l, r, n")

    driver.close()

except Exception as e:
    print(f"\n⚠️ Erro ao salvar no Neo4j: {e}")
    print("Verifique se o Neo4j está rodando e as credenciais estão corretas")

print("\n" + "=" * 60)