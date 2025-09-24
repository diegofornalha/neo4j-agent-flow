# 🚀 Quick Start - API em 5 Minutos

## 📋 Pré-requisitos

```bash
# Verificar Python
python --version  # 3.10+

# Verificar Node (para frontend)
node --version    # 18+
```

## 🔧 Instalação Rápida

### 1️⃣ Clone o Projeto
```bash
git clone https://github.com/seu-usuario/neo4j-agent-flow.git
cd neo4j-agent-flow
```

### 2️⃣ Configure Ambiente
```bash
# Criar .env na pasta api/
cd api
cp .env.example .env

# Editar .env
ANTHROPIC_API_KEY=sua_key_aqui
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 3️⃣ Instale Dependências
```bash
# Backend Python
pip install -r requirements.txt

# Frontend (opcional)
cd ../chat
npm install
```

### 4️⃣ Rode a API
```bash
# Voltar para pasta api/
cd ../api

# Rodar servidor
python server.py
```

Saída esperada:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Claude Handler initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## ✅ Teste Rápido

### Teste 1: Health Check
```bash
curl http://localhost:8000/api/health
```

Resposta:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-24T12:00:00",
  "service": "Hackathon Flow Blockchain Agents Proxy",
  "sdk_available": true,
  "sessions_active": 0
}
```

### Teste 2: Primeira Mensagem
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, o que você pode fazer?"}'
```

### Teste 3: Interface Web
Abra no navegador:
```
http://localhost:8000/chat_debug.html
```

## 🎮 Uso Básico

### Python
```python
import requests
import json

# Enviar mensagem
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "Explique Flow Blockchain",
        "project_id": "meu-projeto"
    },
    stream=True
)

# Ler streaming
for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        print(data['content'], end='', flush=True)
```

### JavaScript
```javascript
// Criar EventSource para SSE
const eventSource = new EventSource('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
        message: "Explique Flow Blockchain"
    })
});

// Receber chunks
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.content);
};
```

### cURL com SSE
```bash
# Streaming em tempo real
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "O que é Cadence?"}'
```

## 🔥 Features Rápidas

### 1. Criar Sessão Persistente
```python
# Criar sessão
session_response = requests.post(
    "http://localhost:8000/api/session",
    json={"project_id": "bootcamp"}
)
session_id = session_response.json()["session_id"]

# Usar sessão
requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "Lembre-se disso: Flow é incrível",
        "session_id": session_id
    }
)
```

### 2. Verificar Neo4j (Opcional)
```bash
# Se tiver Neo4j rodando
neo4j status

# Ou use Docker
docker run -d \
  --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 3. Frontend React (Opcional)
```bash
cd chat
npm start
# Abre em http://localhost:3000
```

## 📊 Estrutura de Resposta

```json
{
  "type": "text",
  "content": "Flow é uma blockchain...",
  "session_id": "uuid-aqui",
  "timestamp": "2025-09-24T12:00:00",
  "metadata": {
    "tokens": 150,
    "model": "claude-3-5-sonnet"
  }
}
```

## 🐛 Troubleshooting Rápido

### Erro: "Port 8000 already in use"
```bash
# Matar processo na porta
lsof -i :8000
kill -9 <PID>

# Ou mudar porta
python server.py --port 8001
```

### Erro: "No module named 'fastapi'"
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro: "ANTHROPIC_API_KEY not set"
```bash
# Verificar .env
cat .env | grep ANTHROPIC

# Ou exportar direto
export ANTHROPIC_API_KEY=sua_key_aqui
```

### Erro: "Neo4j connection failed"
```bash
# API funciona sem Neo4j!
# Apenas desabilita persistência
```

## 🎯 Próximos Passos

Agora que está rodando:

1. **Explore os endpoints** - [API Reference](./11_API_ENDPOINTS.md)
2. **Entenda conceitos** - [Basic Concepts](./10_BASIC_CONCEPTS.md)
3. **Customize** - [MCP Tools](./31_MCP_TOOLS.md)
4. **Deploy** - [Production](./43_DEPLOYMENT.md)

## 📈 Checklist de Sucesso

- [ ] API rodando em localhost:8000
- [ ] Health check retorna "healthy"
- [ ] Primeira mensagem respondida
- [ ] Interface web funcionando
- [ ] SSE streaming visível

**Completou todos?** +3 pontos! 🎉

## 💡 Dicas Pro

1. **Use `--reload` para desenvolvimento**
   ```bash
   uvicorn server:app --reload
   ```

2. **Ative logs detalhados**
   ```bash
   export LOG_LEVEL=DEBUG
   python server.py
   ```

3. **Monitor em tempo real**
   ```bash
   tail -f logs/api.log
   ```

---

**Próximo**: [10_BASIC_CONCEPTS.md](./10_BASIC_CONCEPTS.md) - Entenda os conceitos fundamentais!

**Score**: +3 pontos por completar o Quick Start! 🚀