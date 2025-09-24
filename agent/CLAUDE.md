# Neo4j Knowledge Agent - Guia de Seleção de Subagentes

## Visão Geral
Este guia ajuda a selecionar o subagente apropriado para tarefas de gestão de conhecimento. Cada subagente é especializado em operações específicas do bootcamp Claude CODE SDK.

## Subagentes Disponíveis

### 1. knowledge-extractor
**Propósito**: Especialista em extrair conhecimento de textos e conectar com o bootcamp

**Use este agente quando:**
- Analisar documentação ou código
- Extrair conceitos de materiais de estudo
- Identificar gaps de conhecimento
- Processar conteúdo do bootcamp
- Conectar novos conceitos com existentes

**Exemplos:**
- "Extraia conceitos deste código Python"
- "O que posso aprender deste exemplo de MCP?"
- "Analise esta documentação sobre hooks"
- "Identifique gaps neste exercício"

### 2. relationship-finder
**Propósito**: Descobrir conexões entre conceitos no grafo de conhecimento

**Use este agente quando:**
- Buscar relacionamentos entre conceitos
- Identificar pré-requisitos de aprendizado
- Encontrar conceitos relacionados
- Mapear dependências de conhecimento
- Validar entendimento cross-language

**Exemplos:**
- "Como MCP se relaciona com Neo4j Agent?"
- "Quais conceitos preciso antes de Hooks?"
- "Mostre conexões entre Python e TypeScript"
- "Qual o caminho de query() até Score 100?"

### 3. pattern-analyzer
**Propósito**: Analisar padrões de aprendizado e progresso

**Use este agente quando:**
- Avaliar progresso do bootcamp
- Identificar padrões de erro
- Detectar tendências de aprendizado
- Analisar velocidade de progresso
- Prever tempo para conclusão

**Exemplos:**
- "Qual meu padrão de aprendizado?"
- "Estou progredindo rápido o suficiente?"
- "Quais erros estou repetindo?"
- "Quando vou atingir Score 75?"

### 4. learning-synthesizer
**Propósito**: Sintetizar aprendizados e gerar insights

**Use este agente quando:**
- Consolidar conhecimento adquirido
- Gerar resumos de aprendizado
- Criar insights personalizados
- Preparar revisões de conteúdo
- Produzir relatórios de progresso

**Exemplos:**
- "Resuma o que aprendi esta semana"
- "Quais insights emergiram dos exercícios?"
- "Crie um resumo de MCP Protocol"
- "Gere relatório do meu progresso"

## Formato de Saída

### Para Conceitos
```markdown
📚 **Conceito Identificado**: query() function
- **Tipo**: Skill fundamental
- **Score Impact**: +5 pontos
- **Semana**: 1
- **Status**: ✅ Dominado

Relacionamentos:
- PARTE_DE → Claude Code SDK
- PREREQUISITO_PARA → ClaudeSDKClient
```

### Para Gaps
```markdown
⚠️ **Gap Crítico**: MCP Protocol
- **Urgência**: ALTA
- **Score Impact**: -15 pontos
- **Bloqueando**: Neo4j Agent, Email Agent

Ação Recomendada:
1. Estudar CONCEITOS/04_mcp_protocol.md
2. Implementar primeira MCP tool
3. Validar em exercício prático
```

### Para Progresso
```markdown
📊 **Status do Bootcamp**
- **Score**: 45/100 (45%)
- **Semana**: 1/12
- **Conceitos**: 12/50 completos

Próximos Marcos:
- Score 60: Completar fundamentos (+2 semanas)
- Score 75: Resolver gaps MCP/Hooks (+4 semanas)
- Score 100: Implementar Neo4j Agent (+12 semanas)
```

## Melhores Práticas

1. **Escolha o agente certo**: Cada um é otimizado para tarefas específicas
2. **Forneça contexto do bootcamp**: Sempre mencione score atual e gaps
3. **Use referências cruzadas**: Conecte Python ↔ TypeScript
4. **Rastreie impacto no score**: Cada ação afeta o progresso
5. **Priorize gaps críticos**: MCP e Hooks bloqueiam progresso

## Integração com Neo4j MCP

Todos os agentes usam as seguintes MCP tools:

- `mcp__neo4j-memory__search_memories` - Buscar conhecimento
- `mcp__neo4j-memory__create_memory` - Adicionar conceitos
- `mcp__neo4j-memory__create_connection` - Criar relacionamentos
- `mcp__neo4j-memory__get_context_for_task` - Obter contexto
- `mcp__neo4j-memory__learn_from_result` - Registrar aprendizado
- `mcp__neo4j-memory__suggest_best_approach` - Sugerir abordagem

## Contexto Atual do Bootcamp

**Sempre considere:**
- Diego Fornalha, Score 45/100
- Semana 1 de 12
- Gaps: MCP Protocol, Hooks System
- Linguagem: Python (principal), TypeScript (validação)
- Meta: Score 100 em 12 semanas

## Comandos Rápidos

- `/extract <texto>` - Extrair conhecimento
- `/relate <conceito>` - Encontrar relacionamentos
- `/analyze` - Analisar padrões
- `/synthesize` - Sintetizar aprendizados
- `/progress` - Ver progresso do bootcamp
- `/gaps` - Listar gaps críticos
- `/next` - Próximos passos recomendados