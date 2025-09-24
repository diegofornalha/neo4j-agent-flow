# 🚀 Nossa API Neo4j-Agent-Flow

## 📊 Arquitetura do Projeto

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend      │────▶│  FastAPI     │────▶│ Claude SDK  │
│  (HTML/React)   │ SSE │   Server     │     │   Client    │
└─────────────────┘     └──────────────┘     └─────────────┘
                               │                     │
                               ▼                     ▼
                        ┌──────────────┐     ┌─────────────┐
                        │   Neo4j DB   │     │  Claude AI  │
                        │  (Memórias)  │     │   (LLM)     │
                        └──────────────┘     └─────────────┘
```

## 🎯 O Que Nossa API Faz

Nossa API é um **proxy inteligente** que:
1. **Conecta** aplicações web ao Claude Code SDK
2. **Gerencia** sessões de conversa com IA
3. **Armazena** conhecimento no Neo4j
4. **Transmite** respostas em tempo real via SSE

## 📚 Componentes Principais

### 1. Server.py - O Coração da API
```python
# FastAPI com endpoints REST
app = FastAPI(
    title="Neo4j Agent - Hackathon Flow Blockchain Agents Proxy",
    description="Proxy REST que encapsula Claude Code SDK com SSE streaming"
)

# Endpoints principais:
/api/health      # Status do servidor
/api/chat        # Chat com streaming SSE
/api/session     # Gerenciamento de sessões
/api/knowledge   # Integração Neo4j (em desenvolvimento)
```

### 2. ClaudeHandler - Gerenciador de IA
```python
class ClaudeHandler:
    """
    - Pool de conexões otimizado
    - Sessões com histórico
    - Streaming de respostas
    - Integração com MCP Tools
    """

    # Features legais:
    POOL_MAX_SIZE = 10        # Múltiplas conexões
    CONNECTION_MAX_AGE = 60    # Reciclagem automática
    HEALTH_CHECK_INTERVAL = 5  # Monitoramento constante
```

### 3. SessionManager - Controle de Sessões
```python
class ClaudeCodeSessionManager:
    """
    - Limite de sessões simultâneas
    - Garbage collection automático
    - Métricas de uso
    - Persistência opcional
    """
```

## 🔥 Features Exclusivas da Nossa API

### 1. **Streaming em Tempo Real (SSE)**
```javascript
// Frontend recebe respostas em tempo real
const eventSource = new EventSource('/api/chat');
eventSource.onmessage = (event) => {
    const chunk = JSON.parse(event.data);
    // Atualiza UI instantaneamente
};
```

### 2. **Pool de Conexões Inteligente**
- Reutiliza conexões para economia
- Health checks automáticos
- Reciclagem de conexões antigas
- Escala automaticamente

### 3. **Integração Neo4j para Memória**
```python
# Armazena conhecimento automaticamente
async def save_to_neo4j(session_id, message, response):
    """Salva interações como nós de conhecimento"""
    await neo4j_client.create_memory(
        type="conversation",
        user_message=message,
        ai_response=response,
        metadata={...}
    )
```

### 4. **MCP Tools Customizadas**
```python
# Adicione suas próprias ferramentas
@tool
async def flow_blockchain_query(address: str):
    """Consulta informações da blockchain Flow"""
    # Sua lógica aqui
```

## 🎮 Como Usar no Bootcamp

### Exercício 1: Primeira Requisição
```python
import requests

# Chat simples
response = requests.post("http://localhost:8000/api/chat",
    json={
        "message": "Olá, o que é Flow Blockchain?",
        "project_id": "bootcamp-flow"
    }
)
```

### Exercício 2: Sessão com Contexto
```python
# Criar sessão
session_response = requests.post("/api/session",
    json={
        "project_id": "bootcamp-flow",
        "config": {
            "temperature": 0.7,
            "system_prompt": "Você é um expert em Flow Blockchain"
        }
    }
)
session_id = session_response.json()["session_id"]

# Chat com contexto
requests.post("/api/chat",
    json={
        "message": "Me ensine sobre Cadence",
        "session_id": session_id
    }
)
```

### Exercício 3: Integração com Neo4j
```python
# Buscar memórias relacionadas
memories = await neo4j_client.search_memories(
    query="Flow Blockchain",
    label="Learning"
)

# Usar memórias no contexto
enhanced_message = f"""
Contexto anterior: {memories}
Pergunta: {user_message}
"""
```

## 🏗️ Estrutura de Arquivos

```
/api/
├── server.py              # FastAPI principal
├── core/
│   ├── claude_handler.py  # Gerenciador Claude
│   ├── session_manager.py # Controle de sessões
│   └── neo4j_client.py   # Cliente Neo4j
├── sdk/
│   └── claude_code_sdk/   # SDK do Claude
├── middleware/
│   └── exception_middleware.py
└── utils/
    └── logging_config.py
```

## 🔧 Configuração Rápida

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar .env
ANTHROPIC_API_KEY=seu_key_aqui
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 3. Rodar servidor
python server.py

# 4. Testar
curl http://localhost:8000/api/health
```

## 💡 Ideias para Expandir

### 1. **Agente Flow Blockchain**
```python
# Adicione funcionalidades específicas do Flow
async def deploy_contract(code: str):
    """Deploy de smart contract no Flow"""

async def query_nft(address: str):
    """Consulta NFTs de um endereço"""
```

### 2. **Sistema de Filas**
```python
# Para processar múltiplas requisições
from celery import Celery
app = Celery('tasks', broker='redis://localhost')
```

### 3. **WebSockets ao invés de SSE**
```python
# Para comunicação bidirecional
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Chat em tempo real
```

## 📈 Pontuação no Bootcamp

Completando exercícios com nossa API:

| Exercício | Pontos | Descrição |
|-----------|--------|-----------|
| Hello API | +5 | Primeira requisição funcionando |
| Sessão Contextual | +7 | Usar session_id corretamente |
| Integração Neo4j | +10 | Salvar/buscar memórias |
| MCP Tool Custom | +15 | Criar ferramenta própria |
| Deploy Production | +20 | API rodando na nuvem |

## 🐛 Troubleshooting

### Erro: "Connection refused"
```bash
# Verificar se servidor está rodando
ps aux | grep python
# Deve mostrar: python server.py
```

### Erro: "Session not found"
```python
# Sessions expiram após 30 min
# Sempre crie nova sessão se necessário
```

### Erro: "Neo4j connection failed"
```bash
# Verificar se Neo4j está rodando
neo4j status
# Ou usar Docker
docker run -p 7687:7687 neo4j
```

## 🎯 Próximos Passos

1. **Hoje**: Rodar a API localmente
2. **Amanhã**: Fazer primeira integração
3. **Esta Semana**: Criar uma MCP Tool
4. **Próxima**: Integrar com Flow Blockchain

---

**Score ao completar**: +25 pontos! 🚀

*Esta é NOSSA API, construída especificamente para o hackathon Flow Blockchain!*