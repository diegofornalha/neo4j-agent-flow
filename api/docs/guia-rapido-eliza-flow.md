# Guia Rápido para Construir Agentes de IA no Flow com Eliza

Eliza é um framework poderoso para construir agentes de IA que podem interagir com usuários através de linguagem natural. Este tutorial irá guiá-lo através da configuração e implantação de um agente de IA no blockchain Flow usando Eliza. Você aprenderá como criar agentes inteligentes que podem entender e responder a consultas de usuários, enquanto aproveitam a infraestrutura segura e escalável do Flow.

## Objetivos de Aprendizagem

Ao final deste tutorial, você será capaz de:

- Configurar o ambiente de desenvolvimento Eliza
- Configurar e implantar um agente de IA no Flow
- Criar e personalizar configurações de personagens
- Integrar diferentes modelos de IA com seu agente
- Interagir com seu agente de IA através de uma interface web
- Adicionar e desenvolver plugins personalizados para funcionalidade estendida

## Pré-requisitos

Antes de começar com Eliza, certifique-se de ter:

- Node.js 23+ (usar nvm é recomendado)
- pnpm 9+
- Git para controle de versão
- Um editor de código (VS Code, Cursor ou VSCodium recomendados)
- Flow-cli para interação com blockchain Flow

**Nota para usuários Windows:** WSL 2 é obrigatório.

## Instalação

ElizaOnFlow é um wrapper dedicado ao Flow para Eliza, portanto:

- Os plugins deste repositório também são compatíveis com o Eliza original
- Você também pode usar qualquer plugin do Eliza original neste repositório

### Clone o repositório

```bash
# ElizaOnFlow é um wrapper com Eliza original como submódulo
git clone --recurse-submodules https://github.com/onflow/elizaOnFlow.git

# Entrar no diretório
cd elizaOnFlow

# Por favor, faça checkout da branch main que usa a versão mais recente do Eliza original
git checkout main
```

Ou, se você quiser usar o Eliza original, execute:

```bash
# A pasta de personagens do Eliza é um submódulo
git clone --recurse-submodules https://github.com/elizaOs/eliza.git

# Entrar no diretório
cd eliza

# Checkout da versão mais recente
git checkout $(git describe --tags --abbrev=0)
```

Se você já clonou sem submódulos, execute:

```bash
# Buscar submódulos
git submodule update --init --recursive
```

### Instalar dependências

```bash
pnpm install --no-frozen-lockfile
```

⚠️ **Aviso:** Use a opção `--no-frozen-lockfile` apenas quando estiver inicializando o repositório ou atualizando versões de pacotes. Essa prática ajuda a manter consistência nas dependências do projeto.

Se você estiver usando ElizaOnFlow, precisa instalar as dependências dos contratos Cadence do Flow:

```bash
flow deps install
```

Construir todos os pacotes:

```bash
pnpm build
```

## Configurar Ambiente

Copie `.env.example` para `.env` e preencha os valores apropriados.

```bash
cp .env.example .env
```

⚠️ **IMPORTANTE:** No desenvolvimento normal, é uma boa prática usar um `.env` para proteger chaves de API e outras informações sensíveis. Ao trabalhar com crypto, é CRÍTICO ser disciplinado e sempre usá-los, mesmo em projetos de teste ou tutoriais. Se você expuser uma chave de carteira, pode perder tudo nessa carteira imediatamente.

Edite `.env` e adicione seus valores. **NÃO adicione este arquivo ao controle de versão.**

## Escolha Seu Modelo

Eliza suporta múltiplos modelos de IA e você define qual modelo usar dentro do arquivo JSON do personagem. Mas lembre-se, uma vez que escolheu um modelo, precisa configurar a configuração relevante.

### Modelos sugeridos:

#### Usar API para acessar provedores de LLM
- **OpenAI:** defina `modelProvider` como `openai`, e configure `OPENAI_API_KEY` no `.env`
- **Deepseek:** defina `modelProvider` como `deepseek`, e configure `DEEPSEEK_API_KEY` no `.env`
- **Grok:** defina `modelProvider` como `grok`, e configure `GROK_API_KEY` no `.env`

#### Usar inferência local
- **Ollama:** defina `modelProvider` como `ollama`, e configure `OLLAMA_MODEL` no `.env` com o nome do modelo que está usando no ollama

Para escolher o modelo, você precisa definir na configuração do personagem. Por exemplo, para OPENAI, defina `modelProvider: "openai"` no arquivo JSON do personagem ou `modelProvider: ModelProviderName.OPENAI` em character.ts

## Configurar Conta Flow do Agente

Crie uma nova conta Flow para o Agente:

```bash
flow accounts create
```

Se você estiver usando Testnet, pode obter tokens gratuitos no [Flow Faucet](https://faucet.flow.com)

Configure o blockchain Flow no `.env` com a nova conta Flow gerada:

```env
FLOW_ADDRESS=
FLOW_PRIVATE_KEY=
FLOW_NETWORK=       # Padrão: mainnet
FLOW_ENDPOINT_URL=  # Padrão: https://mainnet.onflow.org
```

Para testnet, verifique [Flow's Networks](https://developers.flow.com/tools/flow-cli/deployment/deploy-project-contracts#testnet) para mais informações.

## Crie Seu Primeiro Agente

### Criar um Arquivo de Personagem

Confira o diretório `deps/eliza/characters/` para vários arquivos de personagem para experimentar. Adicionalmente, você pode sobrescrever o `defaultCharacter` do Eliza editando `character.ts`.

Copie um dos arquivos de exemplo de personagem e personalize:

```bash
cp characters/scooby.character.json characters/sample.character.json
```

### Estrutura do Arquivo de Personagem

```json
{
  "name": "MeuAgente",
  "description": "Um agente inteligente para ajudar com Flow blockchain",
  "modelProvider": "openai",
  "voice": {
    "model": "en_US-neutral"
  },
  "bio": [
    "Sou um agente especializado em Flow blockchain",
    "Ajudo desenvolvedores a entender e usar o Flow"
  ],
  "style": {
    "all": [
      "seja útil e amigável",
      "use linguagem clara e simples",
      "forneça exemplos práticos"
    ]
  }
}
```

## Iniciar o Agente

Informe qual personagem você quer executar:

```bash
pnpm start --character="characters/sample.character.json"
```

Ou use `pnpm start:debug` para mais logs de depuração:

```bash
pnpm start:debug --character="characters/sample.character.json"
```

Você pode carregar múltiplos personagens com uma lista separada por vírgulas:

```bash
pnpm start --characters="characters/sample.character.json, characters/scooby.character.json"
```

## Adicionar / Desenvolver Plugins

### Listar plugins disponíveis:
```bash
npx elizaos plugins list
```

### Instalar um plugin:
```bash
npx elizaos plugins add @elizaos-plugins/plugin-NAME
```

### Criar um novo plugin personalizado:

Para criar um novo plugin para seu próprio negócio, você pode consultar o [guia de desenvolvimento de plugins](https://elizaos.github.io/eliza/docs/plugins).

### Estrutura básica de um plugin:

```typescript
import { Plugin, Action } from '@elizaos/core';

export const meuPlugin: Plugin = {
  name: 'meu-plugin',
  description: 'Plugin personalizado para Flow',
  actions: [
    {
      name: 'minhaAcao',
      description: 'Executa uma ação personalizada',
      handler: async (context) => {
        // Lógica da ação aqui
        return { success: true };
      }
    }
  ]
};
```

## Requisitos Adicionais

Você pode precisar instalar Sharp. Se você ver um erro ao iniciar, tente instalá-lo com o seguinte comando:

```bash
pnpm install --include=optional sharp
```

## Interagir com o Agente

Agora você está pronto para iniciar uma conversa com seu agente.

Abra uma nova janela de terminal e execute o servidor http do cliente:

```bash
pnpm start:client
```

Uma vez que o cliente esteja rodando, você verá uma mensagem como esta:

```
➜  Local:   http://localhost:5173/
```

Simplesmente clique no link ou abra seu navegador em `http://localhost:5173/`. Você verá a interface de chat conectar ao sistema, e poderá começar a interagir com seu personagem.

## Problemas Comuns e Soluções

### Erro de versão do Node.js
**Problema:** Versão incompatível do Node.js
**Solução:** Use nvm para instalar e usar Node.js 23+
```bash
nvm install 23
nvm use 23
```

### Erro de dependências
**Problema:** Erro ao instalar dependências
**Solução:** Limpe o cache e reinstale
```bash
pnpm store prune
pnpm install --no-frozen-lockfile
```

### Erro de conexão com Flow
**Problema:** Não consegue conectar ao blockchain Flow
**Solução:** Verifique suas configurações no `.env` e certifique-se de que o endpoint está correto

## Integração com Claude Code SDK

Para integrar o Eliza com o Claude Code SDK do nosso projeto:

```javascript
// Exemplo de integração
import { ClaudeHandler } from './core/claude_handler';

const claudeIntegration = {
  name: 'claude-integration',
  handler: async (message) => {
    const response = await claudeHandler.sendMessage(sessionId, message);
    return response;
  }
};
```

## Conclusão

Neste tutorial, você aprendeu como construir e implantar um agente de IA no blockchain Flow usando Eliza. Você ganhou experiência prática com:

- Configuração do ambiente de desenvolvimento
- Configuração de agentes
- Criação de configurações de personagens
- Integração de modelos de IA
- Desenvolvimento de plugins personalizados

O framework Eliza fornece uma maneira poderosa de criar agentes inteligentes que podem entender e responder a consultas de usuários enquanto aproveitam a infraestrutura segura e escalável do Flow. Ao completar este tutorial, você agora tem a base para construir agentes de IA mais sofisticados e criar experiências únicas de usuário através de personalização de personagem e desenvolvimento de plugins.

---

*Este material faz parte do Bootcamp de AI Agents no Flow Blockchain*