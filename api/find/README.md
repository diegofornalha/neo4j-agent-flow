# 🔍 Flow Name Service (FNS) Integration

## 📋 Visão Geral

Este módulo implementa a integração completa do **Flow Name Service (.find)** com o Neo4j Agent Flow, permitindo:

- 🏷️ **Registro de nomes .find** na testnet
- 🔍 **Resolução** de nomes para endereços
- 👤 **Perfis descentralizados**
- 🎮 **Sistema de Quiz** para nomes premium
- 💰 **Estrutura de preços** em tiers

## 🗂️ Estrutura de Arquivos

```
find/
├── __init__.py           # Exports principais
├── fns_integration.py    # Core do FNS
├── commands.py           # Comandos do chat
├── quiz.py              # Sistema de quiz e badges
├── config.py            # Configurações
└── README.md            # Esta documentação
```

## 🚀 Como Usar

### 1. Importar no Servidor

```python
# server.py
from find import setup_fns_endpoints, FindNameService

# Adicionar endpoints ao FastAPI
fns = await setup_fns_endpoints(app)
```

### 2. Comandos no Chat

O sistema detecta automaticamente comandos FNS:

| Comando | Exemplo | Descrição |
|---------|---------|-----------|
| `resolve` | "resolve alice.find" | Obtém endereço |
| `check` | "check diego.find" | Verifica disponibilidade |
| `register` | "register meunome.find" | Inicia registro |
| `profile` | "perfil de bob.find" | Busca perfil |
| `quiz` | "quiz start" | Inicia quiz para badges |

### 3. Endpoints da API

```bash
# Resolver nome
GET /api/fns/resolve/{name}

# Verificar disponibilidade
GET /api/fns/check/{name}

# Buscar perfil
GET /api/fns/profile/{name}

# Submeter quiz
POST /api/fns/quiz/submit
```

## 💰 Estrutura de Preços

| Tier | Tamanho | Preço Testnet | Preço Mainnet |
|------|---------|---------------|---------------|
| **Exclusivo** | ≤3 chars | 50 FLOW | 500 FLOW |
| **Premium** | 4-5 chars | 15 FLOW | 150 FLOW |
| **Standard** | ≥6 chars | 5 FLOW | 50 FLOW |

## 🎮 Sistema de Quiz

Complete o quiz para desbloquear benefícios:

- **Score < 80%**: Apenas nomes standard (≥6 chars)
- **Score ≥ 80%**: Badge "flow-expert" + 20% desconto
- **Score ≥ 95%**: Badge "flow-master" + 50% desconto

### Questões do Quiz

1. Tamanho mínimo de um nome .find
2. Endereço do contrato na testnet
3. Custo de nomes exclusivos
4. Caracteres permitidos
5. Conceito de reverse lookup

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Rede (testnet ou mainnet)
FNS_NETWORK=testnet

# Contratos
FNS_TESTNET_CONTRACT=0x35717efbbce11c74
FNS_MAINNET_CONTRACT=0x097bafa4e0b48eef

# Access Node
FLOW_ACCESS_NODE=access.devnet.nodes.onflow.org
FLOW_ACCESS_PORT=9000
```

### Obter FLOW na Testnet

1. Acesse: https://faucet.flow.com/fund-account
2. Insira seu endereço Flow
3. Receba FLOW de teste grátis

## 📊 Integração com Chat

### Detecção Automática

O sistema detecta menções a .find e resolve automaticamente:

```
Usuário: "Enviar 10 FLOW para alice.find"
Sistema: Resolve alice.find → 0x123...
Sistema: Executa transferência
```

### Formatação de Respostas

```python
# Resolução
📍 alice.find → 0x1234567890abcdef

# Disponibilidade
🔍 diego.find
Status: ✅ Disponível
Tier: STANDARD
Taxa: 5 FLOW

# Perfil
👤 Perfil de bob.find
Bio: Developer Flow
Avatar: ipfs://...
```

## 🧪 Testes

### Testar Integração

```bash
# Executar testes
python3 find/fns_integration.py

# Output esperado:
🔍 Flow Name Service - Demonstração
💬 Mensagem: 'resolve flowverse.find'
📤 Resposta: ...
```

### Comandos de Teste no Chat

1. "resolve alice.find"
2. "check teste123.find"
3. "quiz start"
4. "perfil de flow.find"

## 📈 Métricas e Cache

O sistema mantém cache local para otimizar:
- Resoluções nome → endereço
- Perfis consultados
- Disponibilidade verificada

Cache expira após 5 minutos.

## 🔗 Recursos Externos

- [Find Labs](https://find.xyz)
- [Documentação .find](https://docs.find.xyz)
- [Flow Faucet](https://faucet.flow.com)
- [Flowscan Explorer](https://flowscan.org)

## 🚨 Troubleshooting

| Problema | Solução |
|----------|---------|
| API .find offline | Sistema usa fallback para contratos diretos |
| Nome inválido | Verificar: 3-16 chars, lowercase, alfanumérico |
| Sem FLOW para registro | Usar faucet: https://faucet.flow.com |
| Quiz não funciona | Verificar conexão com backend |

## 🎯 Roadmap

- [ ] Integração com FCL para chamadas diretas ao contrato
- [ ] Sistema de notificações para nomes expirando
- [ ] Marketplace de nomes secundário
- [ ] Integração com NFTs de perfil
- [ ] Analytics de uso de nomes

## 📝 Notas para o Hackathon

### Diferencial Competitivo

1. **UX Melhorada**: Nomes legíveis vs endereços hex
2. **Gamificação**: Quiz para badges e descontos
3. **Cache Inteligente**: Performance otimizada
4. **Fallback Robusto**: Funciona mesmo com API offline

### Pontos de Integração

- ✅ Chat reconhece comandos FNS
- ✅ API REST com endpoints dedicados
- ✅ Widget de saldo mostra nome .find
- ✅ Quiz integrado para badges

---

**Desenvolvido para**: Flow AI Hackathon 2024
**Objetivo**: Tornar Web3 mais acessível com identidades legíveis