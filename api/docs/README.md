# 📚 Bootcamp AI Agents no Flow Blockchain

Bem-vindo ao material completo do Bootcamp de AI Agents no Flow Blockchain! Este repositório contém todos os recursos necessários para aprender a construir agentes inteligentes que interagem com o blockchain Flow.

## 🎯 Objetivo do Bootcamp

Capacitar desenvolvedores a criar agentes de IA autônomos que podem:
- Executar transações blockchain automaticamente
- Interagir com smart contracts através de linguagem natural
- Gerenciar ativos digitais e NFTs
- Automatizar fluxos de trabalho DeFi complexos

## 📖 Conteúdo do Bootcamp

### 1. [Introdução aos AI Agents no Flow](./bootcamp-ai-agents-flow.md)
- O que são AI Agents e sua evolução
- Benefícios dos agentes no blockchain
- Casos de uso práticos
- Arquitetura de implementação

### 2. [Guia Rápido Eliza no Flow](./guia-rapido-eliza-flow.md)
- Configuração do ambiente Eliza
- Criação do primeiro agente conversacional
- Personalização de personagens
- Integração com modelos de IA

### 3. [Desenvolvimento de Plugins Eliza](./guia-desenvolvimento-plugins-eliza.md)
- Criação de plugins personalizados
- Implementação de ações e serviços
- Injeção de dependência
- Publicação no registro de plugins

### 4. [AgentKit no Flow](./guia-agentkit-flow.md)
- Configuração rápida com AgentKit
- Integração com Claude e GPT-4
- Configuração de carteiras e transações
- Exemplos práticos de uso

### 5. [Flow MCP Protocol](./flow-mcp-protocol.md)
- Entendendo o Model Context Protocol
- Arquitetura e componentes
- Ferramentas disponíveis
- Segurança e melhores práticas

### 6. [Usar Flow MCP no Cursor](./usar-flow-mcp-cursor.md)
- Instalação e configuração no Cursor
- Consultas blockchain direto no editor
- Exemplos práticos de uso
- Solução de problemas

## 🚀 Como Começar

### Pré-requisitos Gerais
- Node.js 23+ (recomendado usar nvm)
- pnpm 9+
- Git
- Editor de código (VS Code, Cursor ou VSCodium)
- Flow CLI

### Início Rápido

1. **Clone este repositório:**
```bash
git clone https://github.com/seu-usuario/neo4j-agent-flow.git
cd neo4j-agent-flow
```

2. **Instale as dependências:**
```bash
# Para o servidor Python
cd api
pip install -r requirements.txt

# Para projetos Node.js
pnpm install
```

3. **Configure o ambiente:**
```bash
cp .env.example .env
# Edite .env com suas chaves de API
```

4. **Inicie o servidor de desenvolvimento:**
```bash
# Servidor API
python server.py

# Interface de chat
Abra chat_debug.html no navegador
```

## 🛠️ Stack Tecnológica

### Blockchain
- **Flow Blockchain** - Blockchain rápido e escalável para NFTs e dApps
- **Cadence** - Linguagem de smart contracts do Flow
- **Flow EVM** - Compatibilidade com Ethereum

### Frameworks de AI Agents
- **Eliza** - Framework para agentes conversacionais
- **AgentKit** - Toolkit modular para desenvolvimento rápido
- **Langchain** - Orquestração de LLMs

### Modelos de IA
- **Claude (Anthropic)** - Modelo principal recomendado
- **GPT-4 (OpenAI)** - Alternativa poderosa
- **Ollama** - Modelos locais open source

### Ferramentas de Desenvolvimento
- **Cursor** - Editor com IA integrada
- **Flow MCP** - Protocol para integração com IDEs
- **Claude Code SDK** - SDK para automação

## 📝 Estrutura do Projeto

```
neo4j-agent-flow/
├── api/                    # Servidor FastAPI
│   ├── core/              # Handlers e lógica principal
│   ├── sdk/               # Claude Code SDK
│   └── server.py          # Servidor principal
├── docs/                  # Documentação do bootcamp
│   ├── bootcamp-ai-agents-flow.md
│   ├── guia-rapido-eliza-flow.md
│   ├── guia-desenvolvimento-plugins-eliza.md
│   ├── guia-agentkit-flow.md
│   ├── flow-mcp-protocol.md
│   └── usar-flow-mcp-cursor.md
├── chat_debug.html        # Interface de teste
└── .env                   # Configurações (não versionado)
```

## 💡 Exemplos de Projetos

### Agente de Trading DeFi
```javascript
// Agente que monitora e executa trades automaticamente
const agent = createAgent({
  name: "DeFi Trader",
  model: "claude-3-5-haiku",
  tools: [checkPrice, executeTrade, manageLiquidity]
});
```

### Assistente de NFT
```javascript
// Agente que gerencia coleções de NFT
const nftAgent = new ElizaAgent({
  personality: "NFT Expert",
  actions: [mintNFT, transferNFT, listOnMarketplace]
});
```

### Automatizador de Contratos
```javascript
// Agente que interage com smart contracts
const contractAgent = createReactAgent({
  llm: new ChatAnthropic(),
  tools: [deployContract, callMethod, queryEvents]
});
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📖 Recursos Adicionais

### Documentação Oficial
- [Flow Developers](https://developers.flow.com)
- [Eliza Framework](https://elizaos.github.io/eliza)
- [AgentKit Docs](https://docs.agentkit.com)
- [Claude API](https://docs.anthropic.com)

### Comunidade
- [Flow Discord](https://discord.gg/flow)
- [Flow Forum](https://forum.flow.com)
- [GitHub Discussions](https://github.com/onflow/flow/discussions)

### Tutoriais em Vídeo
- [Flow YouTube](https://youtube.com/@flow)
- [Workshops gravados](https://flow.com/workshops)

## 🎓 Certificação

Ao completar o bootcamp, você estará apto a:
- ✅ Criar agentes de IA funcionais no Flow
- ✅ Desenvolver plugins personalizados
- ✅ Integrar múltiplos modelos de IA
- ✅ Executar operações blockchain automatizadas
- ✅ Construir interfaces conversacionais
- ✅ Deploy em produção

## 📊 Status do Projeto

- ✅ Material traduzido e adaptado
- ✅ Servidor API funcional
- ✅ Interface de debug operacional
- ✅ Integração com Neo4j para persistência
- 🚧 Exemplos adicionais em desenvolvimento
- 🚧 Vídeos tutoriais planejados

## 📬 Contato e Suporte

- **Issues:** [GitHub Issues](https://github.com/seu-usuario/neo4j-agent-flow/issues)
- **Discussões:** [GitHub Discussions](https://github.com/seu-usuario/neo4j-agent-flow/discussions)
- **Email:** suporte@seudominio.com

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](../LICENSE) para mais detalhes.

---

**Hackathon Flow Blockchain 2024** 🚀

*Construindo o futuro dos agentes autônomos no blockchain*