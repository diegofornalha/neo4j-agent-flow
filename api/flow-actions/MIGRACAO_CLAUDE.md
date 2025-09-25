# 🔄 Plano de Migração: LiteLLM → Claude SDK

## 📋 Sumário Executivo

O projeto flow-actions usa LiteLLM como gateway de API para modelos de linguagem, com cobrança automática via Flow blockchain. Vamos remover completamente o LiteLLM e integrar com nosso Claude Code SDK existente.

## 🔍 Análise do Sistema Atual

### Arquitetura LiteLLM
```
Usuário → LiteLLM API → Oracle → Flow Blockchain → Pagamento
           ↓
       Webhook/Polling
           ↓
       Usage Tracking
```

### Componentes Principais

#### 1. **Oracle de Uso** (`litellm-usage-oracle.js`)
- Busca dados de uso da API LiteLLM
- Converte para formato FDC (Flare Data Connector)
- Submete triggers para Flow blockchain
- **Métodos principais:**
  - `fetchLiteLLMUsage()` - Busca uso da API
  - `createFDCTrigger()` - Formata para blockchain
  - `submitToFlow()` - Envia para Flow

#### 2. **Webhook Receiver** (`litellm-webhook-receiver.js`)
- Recebe callbacks em tempo real do LiteLLM
- Verifica assinaturas
- Processa pagamentos automáticos
- **Endpoints:**
  - `/webhook/usage` - Uso individual
  - `/webhook/usage/batch` - Uso em lote

#### 3. **Smart Contracts Cadence**
- `DynamicEntitlements.cdc` - Sistema de cobrança com entitlements
- `UsageBasedSubscriptions.cdc` - Gerencia assinaturas
- `FlareOracleVerifier.cdc` - Verifica dados do oracle
- **Estes são genéricos e podem ser reutilizados!**

## 🎯 Plano de Migração

### Fase 1: Criar Adaptador Claude
```javascript
// claude-usage-oracle.js
class ClaudeUsageOracle {
    async fetchClaudeUsage(sessionId, timeRange = '24h') {
        // Buscar do Neo4j em vez de API externa
        const usage = await neo4j.query(`
            MATCH (s:Session {id: $sessionId})-[:HAS_MESSAGE]->(m:Message)
            WHERE m.timestamp > timestamp() - duration('PT24H')
            RETURN count(m) as messages, sum(m.tokens) as totalTokens
        `, { sessionId });

        return {
            sessionId,
            totalTokens: usage.totalTokens,
            messages: usage.messages,
            model: 'claude-3-opus',
            timestamp: Date.now()
        };
    }
}
```

### Fase 2: Webhook para Claude
```javascript
// claude-webhook-handler.js
class ClaudeWebhookHandler {
    async processMessage(sessionId, message, response) {
        // Calcular tokens usados
        const tokens = this.countTokens(message + response);

        // Atualizar uso no blockchain
        await this.updateOnchainUsage(sessionId, tokens);

        // Salvar no Neo4j
        await this.saveToGraph(sessionId, message, response, tokens);
    }
}
```

### Fase 3: Remover Dependências LiteLLM

#### Arquivos para DELETAR:
```
scripts/fdc-integration/
├── litellm-usage-oracle.js ❌
├── litellm-webhook-receiver.js ❌
├── litellm-polling-monitor.js ❌
├── litellm-flare-connector.js ❌
├── test-litellm-endpoints.js ❌
└── explore-litellm-api.js ❌
```

#### Arquivos para CRIAR:
```
scripts/claude-integration/
├── claude-usage-oracle.js ✅
├── claude-webhook-handler.js ✅
├── claude-neo4j-tracker.js ✅
└── claude-flow-billing.js ✅
```

#### Arquivos para MODIFICAR:

1. **package.json**
```json
{
  "name": "claude-flow-connector",  // Renomear
  "scripts": {
    "start": "node claude-flow-billing.js"  // Mudar entry point
  },
  "dependencies": {
    "@onflow/fcl": "^1.20.0",
    "@onflow/types": "^1.4.1",
    "neo4j-driver": "^5.0.0",  // Adicionar
    "axios": "^1.6.0",
    "dotenv": "^16.3.0"
  }
}
```

2. **.env.example**
```env
# Claude Configuration
CLAUDE_API_KEY=your_claude_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Flow Configuration (manter)
FLOW_CONTRACT_ADDRESS=0x6daee039a7b9c2f0
FLOW_NETWORK=testnet  # Mudamos para testnet!

# Flare Configuration (manter)
FLARE_ENDPOINT=https://coston2-api.flare.network/ext/bc/C/rpc
```

3. **Smart Contracts** (Apenas renomear referências)
```cadence
// DynamicEntitlements.cdc - linha 199
access(all) resource ClaudeHandler: FlareFDCTriggers.TriggerHandler {
    // Mudar de LiteLLMHandler para ClaudeHandler
}
```

## 📊 Mapeamento de Funcionalidades

| LiteLLM | Claude SDK | Status |
|---------|------------|--------|
| API Key management | Session management | ✅ Temos |
| Usage tracking via API | Usage tracking via Neo4j | ✅ Temos |
| Webhook endpoints | SSE streaming | ✅ Temos |
| Batch processing | Message batching | 🔄 Adaptar |
| Cost calculation | Token counting | 🔄 Implementar |
| Oracle submission | Flow integration | ✅ Reusar |

## 🚀 Implementação Passo a Passo

### Passo 1: Backup
```bash
cp -r scripts/fdc-integration scripts/fdc-integration.backup
```

### Passo 2: Criar Claude Oracle
```javascript
// claude-usage-oracle.js
const neo4j = require('neo4j-driver');
const fcl = require('@onflow/fcl');

class ClaudeUsageOracle {
    constructor(config) {
        this.driver = neo4j.driver(
            config.neo4jUri,
            neo4j.auth.basic(config.neo4jUser, config.neo4jPassword)
        );

        // Configurar Flow (reusar do LiteLLM)
        this.flowConfig = config.flow;
    }

    // Implementar métodos equivalentes
}
```

### Passo 3: Integrar com nosso Server
```python
# server.py - adicionar tracking
async def handle_message(session_id, message):
    response = await claude.process(message)

    # Novo: trackear uso
    tokens = count_tokens(message + response)
    await track_usage(session_id, tokens)

    return response

async def track_usage(session_id, tokens):
    # Enviar para Flow via oracle
    oracle.submit_usage(session_id, tokens)
```

### Passo 4: Testar Flow Actions
```bash
# Testar transações existentes
flow transactions send cadence/transactions/increment_fi_restake.cdc --network testnet

# Testar novo oracle
node scripts/claude-integration/test-oracle.js
```

## 💡 Vantagens da Migração

1. **Simplificação**: Remove camada intermediária (LiteLLM)
2. **Controle Total**: Gerenciamos nosso próprio uso
3. **Neo4j Integration**: Uso já está no grafo
4. **Custo Zero**: Não pagamos por proxy de API
5. **Flow Actions Nativas**: Integração direta com blockchain

## ⚠️ Riscos e Mitigação

| Risco | Mitigação |
|-------|-----------|
| Perder funcionalidade de multi-modelo | Focar apenas em Claude (nosso diferencial) |
| Complexidade de tracking | Neo4j já faz isso naturalmente |
| Integração com Flare | Reusar código existente |

## 🎯 Resultado Final

### Antes (LiteLLM)
```
User → LiteLLM → Multiple LLMs → Oracle → Flow
         ↑
      API Keys
```

### Depois (Claude SDK)
```
User → Claude SDK → Neo4j → Oracle → Flow
           ↑
       Session ID
```

## 📝 Checklist de Migração

- [ ] Fazer backup completo
- [ ] Criar `claude-usage-oracle.js`
- [ ] Adaptar webhook handler
- [ ] Modificar smart contracts (renomear handlers)
- [ ] Atualizar package.json
- [ ] Remover arquivos LiteLLM
- [ ] Testar oracle com Claude
- [ ] Testar Flow Actions
- [ ] Testar billing automático
- [ ] Documentar nova API

## 🔗 Integração com Neo4j Agent Flow

Nossa arquitetura final:
```
Frontend Chat
     ↓
Claude SDK + Neo4j (memória)
     ↓
Usage Oracle (tracking)
     ↓
Flow Blockchain (billing)
     ↓
Flow Actions (automação)
```

## 🚨 Próximos Passos Imediatos

1. **Confirmar remoção**: Deletar todos arquivos LiteLLM
2. **Implementar oracle**: Criar versão Claude
3. **Testar integração**: Verificar Flow Actions funcionando
4. **Documentar**: Atualizar README com nova arquitetura

---

**Status**: Pronto para iniciar migração! 🚀