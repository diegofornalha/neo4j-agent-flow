# Começando com AgentKit no Flow

AgentKit é um toolkit modular para desenvolvedores, agnóstico ao ecossistema, que permite construir, implantar e iterar rapidamente sobre agentes de IA usando ambientes pré-configurados e templates prontos para uso.

Neste guia, você configurará seu próprio agente personalizado rodando na testnet compatível com EVM do Flow, alimentado por Langchain e Claude LLM da Anthropic.

## Início Rápido - Começando do Zero

Abra seu terminal e execute:

```bash
npm create onchain-agent@latest
```

Siga a configuração interativa:

1. Digite `y` para prosseguir, depois pressione Enter
2. Selecione seu framework: **Langchain**
3. Escolha sua rede: **EVM**
4. Configure o Chain ID personalizado:
   - `545` para Flow Testnet
   - `747` para Flow Mainnet
5. Endpoint JSON-RPC:
   - `https://testnet.evm.nodes.onflow.org`

## Configuração do Projeto

Uma vez que seu scaffold esteja pronto:

```bash
cd onchain-agent
npm install
```

Agora abra o projeto em seu IDE preferido (ex: Cursor).

## Configuração do Ambiente

1. Crie um arquivo `.env.local` (ou edite o gerado)
2. Adicione suas chaves de API (usaremos Anthropic aqui)

Você também pode usar OpenAI, DeepSeek, ou qualquer outro LLM suportado.

### Obter sua Chave de API Anthropic

1. Vá para [Anthropic Console](https://console.anthropic.com)
2. Crie uma conta e compre créditos
3. Clique em **Create Key**, nomeie-a e copie a chave de API
4. Adicione ao seu `.env.local`:

```env
ANTHROPIC_API_KEY=sua_chave_api_aqui
```

### Configuração de Carteira com MetaMask

1. Adicione Flow Testnet ao MetaMask
2. Use o [Faucet](https://faucet.flow.com) para financiar sua carteira
3. Obtenha sua chave privada:
   - Clique no menu `...` no MetaMask > Detalhes da Conta
   - Digite sua senha, copie a chave privada
4. Adicione ao `.env.local`:

```env
PRIVATE_KEY=sua_chave_privada_aqui
```

Seu `.env.local` deve ficar assim:

```env
PRIVATE_KEY=...
ANTHROPIC_API_KEY=...
```

Agora execute:

```bash
mv .env.local .env
npm run dev
```

Visite seu servidor local:

```
http://localhost:3000
```

## Configure seu LLM

Se seu agente ainda não responder — sem problemas! Você ainda precisa configurar seu LLM e bibliotecas cliente.

### Escolha um Modelo

Langchain suporta muitos LLMs ([lista completa aqui](https://js.langchain.com/docs/integrations/llms/)).

Para este exemplo, usaremos o `claude-3-5-haiku-20241022` da Anthropic, um modelo leve e acessível. Alternativamente, DeepSeek é altamente recomendado para uso econômico.

### Atualize create-agent.ts

Mude o modelo padrão de OpenAI:

```typescript
const llm = new ChatOpenAI({ model: 'gpt-4o-mini' });
```

Para Anthropic:

```typescript
import { ChatAnthropic } from '@langchain/anthropic';

const llm = new ChatAnthropic({ model: 'claude-3-5-haiku-20241022' });
```

Instale o pacote:

```bash
npm install @langchain/anthropic
```

## Configurar Flow e Viem Wallet

### Atualizar a Lógica do Provedor Faucet

Mude isto:

```typescript
const canUseFaucet = walletProvider.getNetwork().networkId == 'base-sepolia';
```

Para:

```typescript
const canUseFaucet = walletProvider.getNetwork().networkId == 'flow-testnet';
```

### Adicionar Mensagem de Contexto Flow ao Agente

Isso dá ao seu agente contexto sobre a testnet Flow:

```typescript
const flowContextMessage = canUseFaucet
  ? `
  Você está agora operando na testnet do blockchain Flow usando uma carteira Viem. Flow é um blockchain rápido,
  descentralizado e amigável ao desenvolvedor, projetado para NFTs, jogos e aplicativos.

  Fatos importantes sobre o Flow:
  - Flow usa um mecanismo de consenso proof-of-stake
  - O token nativo é FLOW
  - Flow tem uma arquitetura única multi-role para alta vazão
  - A testnet é compatível com EVM (funciona com MetaMask + Viem)
  - URL RPC: https://testnet.evm.nodes.onflow.org
  - Chain ID: 545

  Seu endereço de carteira é ${await walletProvider.getAddress()}.
`
  : '';
```

Em seguida, injete no modificador de mensagem do agente:

```typescript
agent = createReactAgent({
  llm,
  tools,
  checkpointSaver: memory,
  messageModifier: `
    Você é um agente útil interagindo com a testnet do blockchain Flow usando uma carteira Viem.
    A testnet Flow suporta EVM, então você pode usar ferramentas compatíveis com Ethereum.
    ${flowContextMessage}

    Antes de sua primeira ação, verifique os detalhes da carteira. Se você ver um erro 5XX,
    peça ao usuário para tentar novamente mais tarde.
    Se uma tarefa não for suportada, informe o usuário e aponte para CDP SDK + AgentKit em:
    https://docs.cdp.coinbase.com ou https://developers.flow.com.

    Seja conciso, útil e evite repetir descrições de ferramentas a menos que solicitado.
  `,
});
```

## Pronto!

Você agora tem um agente de IA funcional conectado à testnet Flow usando AgentKit!

Você pode enviar tokens do faucet para sua carteira e começar a testar interações com smart contracts ou fluxos de trabalho onchain.

## Projeto Inicial

Quer pular a configuração?

[Fork o Flow AgentKit Starter](https://github.com/onflow/agentkit-starter)

Este starter inclui toda a configuração necessária para começar a construir imediatamente no Flow.

## Adicionando AgentKit a um Projeto Existente

Já tem um projeto e quer adicionar AgentKit? Siga estes passos para integrá-lo ao seu código existente:

### Instalar o Pacote

Execute este comando no diretório raiz do seu projeto:

```bash
npm install onchain-agent@latest
```

Isso irá:
- Baixar e instalar a versão mais recente do pacote onchain-agent
- Adicioná-lo à seção dependencies do seu package.json
- Atualizar sua pasta node_modules adequadamente

### Configurar Ambiente

Crie ou atualize seu arquivo `.env` com as chaves de API necessárias:

```env
PRIVATE_KEY=sua_chave_privada_carteira
ANTHROPIC_API_KEY=sua_chave_api_anthropic
# Ou outras chaves de API de LLM

# Configure seus endpoints RPC para Flow:
FLOW_TESTNET_RPC_URL=https://testnet.evm.nodes.onflow.org
FLOW_MAINNET_RPC_URL=https://mainnet.evm.nodes.onflow.org
```

### Integrar AgentKit no Seu Código

Importe e configure AgentKit em sua aplicação:

```typescript
// Importar componentes do AgentKit
import { createReactAgent, ChatAnthropic } from 'onchain-agent';
import { createWalletClient, http, createPublicClient } from 'viem';

// Configurar seu provedor de carteira Flow
const walletClient = createWalletClient({
  transport: http('https://testnet.evm.nodes.onflow.org'),
  chain: {
    id: 545, // Flow Testnet
    name: 'Flow Testnet',
  },
  account: suaChavePrivada,
});

// Configurar o LLM
const llm = new ChatAnthropic({
  model: 'claude-3-5-haiku-20241022',
});

// Criar seu agente
const agent = createReactAgent({
  llm,
  tools: suasFerramentasSelecionadas,
  // Configuração adicional
});

// Usar o agente em sua aplicação
// ...
```

### Adicionar Ferramentas Especializadas (Opcional)

Para adicionar ferramentas blockchain especializadas ao seu agente:

```typescript
import { viem, ViemToolConfig } from 'onchain-agent';

// Configurar ferramentas Viem para Flow
const viemTools = viem.createTools({
  chain: {
    id: 545,
    name: 'Flow Testnet',
  },
  transport: http('https://testnet.evm.nodes.onflow.org'),
} as ViemToolConfig);

// Adicionar essas ferramentas ao seu agente
const agent = createReactAgent({
  llm,
  tools: [
    ...viemTools,
    // Outras ferramentas
  ],
});
```

## Exemplos de Uso

### Verificar Saldo

```typescript
async function verificarSaldo(address: string) {
  const response = await agent.invoke({
    messages: [
      {
        role: 'user',
        content: `Verifique o saldo de FLOW para o endereço ${address}`,
      },
    ],
  });
  return response;
}
```

### Executar Transação

```typescript
async function enviarFlow(to: string, amount: string) {
  const response = await agent.invoke({
    messages: [
      {
        role: 'user',
        content: `Envie ${amount} FLOW para ${to}`,
      },
    ],
  });
  return response;
}
```

### Interagir com Smart Contract

```typescript
async function chamarContrato(contractAddress: string, method: string, params: any[]) {
  const response = await agent.invoke({
    messages: [
      {
        role: 'user',
        content: `Chame o método ${method} no contrato ${contractAddress} com parâmetros ${JSON.stringify(params)}`,
      },
    ],
  });
  return response;
}
```

## Recursos

- [Documentação AgentKit](https://docs.agentkit.com)
- [Guia Flow EVM](https://developers.flow.com/evm)
- [Integrações LLM Langchain](https://js.langchain.com/docs/integrations/llms/)
- [Comparação de Modelos Anthropic](https://docs.anthropic.com/models)

## Conclusão

AgentKit fornece uma maneira poderosa de criar agentes de IA que podem interagir com o blockchain Flow. Com a configuração completa, você pode:

- Executar transações automaticamente
- Consultar dados blockchain em tempo real
- Interagir com smart contracts
- Criar fluxos de trabalho complexos onchain
- Integrar com múltiplos modelos de IA

Feliz hacking no Flow!

---

*Este material faz parte do Bootcamp de AI Agents no Flow Blockchain*