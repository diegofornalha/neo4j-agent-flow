# 🎓 Conceitos Básicos - Neo4j Agent Flow API

## 🧠 Conceitos Fundamentais para Diego

### 1. **O Problema Central**

```
Você (Diego) quer usar Claude AI em uma aplicação web
                    ↓
        MAS Claude SDK só funciona em CLI
                    ↓
        SOLUÇÃO: Nossa API faz a ponte!
```

### 2. **Como Nossa API Resolve**

```python
# Sem nossa API (não funciona no browser):
from claude_code_sdk import query  # ❌ Browser não tem Python!

# Com nossa API (funciona em qualquer lugar):
fetch('http://localhost:8000/api/chat', {  # ✅ Funciona no browser!
    method: 'POST',
    body: JSON.stringify({ message: "Olá Claude" })
})
```

## 🔄 Fluxo de Dados Completo

```
1. Browser envia mensagem
        ↓
2. FastAPI recebe via HTTP
        ↓
3. ClaudeHandler processa
        ↓
4. SessionManager mantém contexto
        ↓
5. ConnectionPool otimiza recursos
        ↓
6. Claude SDK comunica com Claude AI
        ↓
7. Resposta volta em streaming (SSE)
        ↓
8. Neo4j salva o conhecimento
        ↓
9. Browser mostra resposta em tempo real
```

## 💡 Conceitos Chave Explicados

### 📡 **SSE (Server-Sent Events)**

SSE permite que o servidor "empurre" dados para o cliente em tempo real:

```javascript
// Cliente escuta eventos
const eventSource = new EventSource('/api/chat');

// Servidor envia chunks
yield f"data: {json.dumps({'content': 'Olá'})}\n\n"
yield f"data: {json.dumps({'content': ' Diego'})}\n\n"
yield f"data: {json.dumps({'content': '!'})}\n\n"

// Resultado no browser: "Olá Diego!" (aparece letra por letra)
```

### 🎯 **Session Management**

Mantém contexto entre mensagens:

```python
# Primeira mensagem
"Meu nome é Diego"  # Session ID: abc-123

# Segunda mensagem (mesma sessão)
"Qual é meu nome?"  # Session ID: abc-123
# Claude responde: "Seu nome é Diego"

# Nova sessão (sem contexto)
"Qual é meu nome?"  # Session ID: xyz-789
# Claude responde: "Não sei seu nome"
```

### 🏊 **Connection Pool**

Reutiliza conexões para economizar recursos:

```python
# Sem pool (ineficiente):
def handle_request():
    client = create_claude_client()  # Cria nova conexão
    response = client.query(...)
    client.close()  # Fecha conexão
    # Problema: criar/fechar é lento!

# Com pool (eficiente):
def handle_request():
    client = pool.get_connection()  # Pega conexão existente
    response = client.query(...)
    pool.return_connection(client)  # Devolve para reutilização
    # Vantagem: 10x mais rápido!
```

### 🧠 **Neo4j Knowledge Graph**

Armazena conhecimento como grafo:

```cypher
// Cria nós de conhecimento
(diego:Person {name: "Diego Fornalha"})
(api:Technology {name: "Neo4j Agent Flow API"})
(flow:Blockchain {name: "Flow"})

// Cria relacionamentos
(diego)-[:ESTÁ_APRENDENDO]->(api)
(diego)-[:INTERESSADO_EM]->(flow)
(api)-[:INTEGRA_COM]->(flow)
```

### 🔧 **MCP Tools**

Adiciona capacidades customizadas ao Claude:

```python
@tool
async def check_flow_balance(address: str):
    """Verifica saldo de FLOW de um endereço"""
    # Claude pode usar esta ferramenta!
    balance = await flow_client.get_balance(address)
    return f"Saldo: {balance} FLOW"
```

## 📚 Componentes da API

### 1. **server.py** - O Maestro
```python
# FastAPI que orquestra tudo
app = FastAPI()

@app.post("/api/chat")
async def chat(message: ChatMessage):
    # 1. Recebe mensagem
    # 2. Delega para ClaudeHandler
    # 3. Retorna streaming SSE
```

### 2. **claude_handler.py** - O Cérebro
```python
class ClaudeHandler:
    # Gerencia comunicação com Claude
    # Mantém pool de conexões
    # Otimiza performance
```

### 3. **session_manager.py** - A Memória
```python
class SessionManager:
    # Controla sessões ativas
    # Garbage collection automático
    # Limites e quotas
```

### 4. **neo4j_client.py** - O Arquivo
```python
class Neo4jClient:
    # Salva conversas
    # Busca conhecimento anterior
    # Cria relações entre conceitos
```

## 🎮 Exemplo Prático para Diego

### Cenário: Chat sobre Flow Blockchain

```python
# 1. Diego pergunta sobre Flow
mensagem = "O que é Flow Blockchain?"

# 2. API processa
async def processar_mensagem(msg):
    # Cria/recupera sessão
    session = await get_or_create_session()

    # Busca contexto no Neo4j
    contexto = await neo4j.search("Flow Blockchain")

    # Envia para Claude com contexto
    response = await claude.query(
        message=msg,
        context=contexto,
        tools=["flow_balance", "flow_nft_info"]
    )

    # Salva no Neo4j
    await neo4j.save_interaction(msg, response)

    # Retorna com streaming
    return stream_response(response)

# 3. Diego recebe resposta em tempo real
# "Flow é uma blockchain rápida e escalável..."
# (aparece palavra por palavra no browser)
```

## 🔍 Por Dentro do Streaming

```python
# Backend envia chunks
async def stream_response(text):
    words = text.split()
    for word in words:
        yield f"data: {{'content': '{word} '}}\n\n"
        await asyncio.sleep(0.05)  # Simula digitação

# Frontend recebe e mostra
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    document.getElementById('chat').innerHTML += data.content;
}
```

## 📊 Vantagens da Nossa Arquitetura

| Característica | Benefício | Para Diego Significa |
|----------------|-----------|---------------------|
| **Proxy Pattern** | Abstrai complexidade | Foco no produto, não na infra |
| **SSE Streaming** | UX moderna | Interface fluida tipo ChatGPT |
| **Connection Pool** | Performance | Respostas rápidas |
| **Neo4j Graph** | Memória persistente | Bot lembra de tudo |
| **MCP Tools** | Extensibilidade | Adicione Flow tools facilmente |

## 🧪 Teste Você Mesmo

### 1. Teste de Sessão
```bash
# Crie uma sessão
SESSION_ID=$(curl -X POST localhost:8000/api/session | jq -r '.session_id')

# Mensagem 1
curl -X POST localhost:8000/api/chat \
  -d "{\"message\": \"Meu nome é Diego\", \"session_id\": \"$SESSION_ID\"}"

# Mensagem 2 (deve lembrar seu nome)
curl -X POST localhost:8000/api/chat \
  -d "{\"message\": \"Qual meu nome?\", \"session_id\": \"$SESSION_ID\"}"
```

### 2. Teste de Streaming
```html
<!-- Salve como test.html e abra no browser -->
<script>
const eventSource = new EventSource('http://localhost:8000/api/chat');
eventSource.onmessage = (e) => {
    document.body.innerHTML += JSON.parse(e.data).content;
};
</script>
```

## 🎯 Checkpoint de Aprendizado

Você entendeu se consegue responder:

1. **Por que precisamos de uma API proxy?**
   - R: Claude SDK não funciona no browser

2. **O que é SSE?**
   - R: Server envia dados em tempo real para cliente

3. **Para que serve o Connection Pool?**
   - R: Reutilizar conexões para performance

4. **Como o Neo4j ajuda?**
   - R: Mantém memória/conhecimento persistente

5. **O que são MCP Tools?**
   - R: Ferramentas customizadas para Claude usar

**Acertou todas?** +5 pontos! 🎉

## 🚀 Próximos Conceitos

- [20_FASTAPI_SERVER.md](./20_FASTAPI_SERVER.md) - Detalhes do servidor
- [21_CLAUDE_HANDLER.md](./21_CLAUDE_HANDLER.md) - Como gerenciamos Claude
- [30_NEO4J_INTEGRATION.md](./30_NEO4J_INTEGRATION.md) - Grafo de conhecimento

---

**Score Total Diego**: 20/100 pontos! 🎯

**Próximo desafio**: Rodar a API e fazer primeira requisição (+10 pontos)