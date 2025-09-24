# Guia de Desenvolvimento de Plugins Eliza

Plugins são uma maneira poderosa de estender a funcionalidade de seus agentes de IA Eliza. Este guia irá orientá-lo através do processo de criação de plugins personalizados que podem aprimorar as capacidades do seu agente, desde utilitários simples até integrações complexas com serviços externos. Você aprenderá como aproveitar o sistema de plugins para criar componentes modulares e reutilizáveis para seus agentes de IA.

## Objetivos de Aprendizagem

Ao final deste tutorial, você será capaz de:

- Criar um novo repositório de plugin a partir do template
- Entender o fluxo de trabalho de desenvolvimento de plugins
- Implementar ações e serviços personalizados
- Integrar plugins com seu agente Eliza
- Registrar e publicar plugins no Registro de Plugins Eliza
- Usar injeção de dependência para melhor arquitetura de plugin

## Pré-requisitos

Antes de começar com Eliza, certifique-se de ter:

- Node.js 23+ (usar nvm é recomendado)
- pnpm 9+
- Git para controle de versão
- Um editor de código (VS Code, Cursor ou VSCodium recomendados)
- Flow-cli para interação com blockchain Flow

**Nota para usuários Windows:** WSL 2 é obrigatório.

## Início Rápido

Por favor, siga o [Guia de Início Rápido](./guia-rapido-eliza-flow.md) para configurar seu ambiente de desenvolvimento.

## Desenvolvimento de Plugins

### Criar um Repositório de Plugin a partir do Template

Visite [Eliza Plugin Template](https://github.com/elizaos/plugin-template) e clique no botão "Use this template" para criar um novo repositório.

Ou você pode criar um novo repositório vazio e copiar os arquivos de alguns exemplos na [organização Eliza Plugins](https://github.com/elizaos-plugins).

**Nota:** O template de plugin Eliza do Flow está usando Injeção de Dependência (@elizaos-plugins/plugin-di), você pode aprender mais sobre a Injeção de Dependência no README.md do plugin. Isso permite que você use Classes em vez de Objects para suas Actions, Providers, Services, etc. Se você não quiser usá-lo, pode seguir os outros exemplos na organização Eliza Plugins.

### Adicionar o Repositório de Plugin ao seu Projeto Eliza

Digamos que você criou um repositório chamado `username/plugin-foo`.

Use submódulos para adicionar o repositório de plugin ao seu projeto Eliza:

```bash
git submodule add https://github.com/username/plugin-foo.git packages/plugin-foo
```

Mude o nome do pacote no `package.json` do plugin para `@elizaos-plugins/plugin-foo`:

```json
{
    "name": "@elizaos-plugins/plugin-foo",
}
```

Adicione o plugin ao `package.json` do agente:

```bash
pnpm add @elizaos-plugins/plugin-foo@'workspace:*' --filter ./agent
```

Verifique o `agent/package.json` para garantir que o plugin foi adicionado, você deve ver algo como:

```json
{
    "dependencies": {
        "@elizaos-plugins/plugin-foo": "workspace:*"
    }
}
```

### Estrutura de um Plugin

#### Estrutura básica de diretórios:
```
plugin-foo/
├── src/
│   ├── index.ts        # Ponto de entrada do plugin
│   ├── actions/        # Ações personalizadas
│   ├── services/       # Serviços do plugin
│   ├── providers/      # Provedores de dados
│   └── types/          # Definições de tipos
├── package.json
├── tsconfig.json
└── README.md
```

#### Exemplo de Plugin Básico:

```typescript
// src/index.ts
import { Plugin } from '@elizaos/core';
import { MinhaAcao } from './actions/minha-acao';
import { MeuServico } from './services/meu-servico';

export const plugin: Plugin = {
    name: 'plugin-foo',
    description: 'Plugin personalizado para funcionalidades foo',
    actions: [MinhaAcao],
    services: [MeuServico],
    providers: [],
};

export default plugin;
```

#### Exemplo de Ação:

```typescript
// src/actions/minha-acao.ts
import { Action, ActionExample, IAgentRuntime, Memory, State } from '@elizaos/core';

export const MinhaAcao: Action = {
    name: 'MINHA_ACAO',
    description: 'Executa uma ação personalizada',
    examples: [
        [
            {
                user: '{{user1}}',
                content: { text: 'Execute minha ação personalizada' },
            },
            {
                user: '{{agentName}}',
                content: {
                    text: 'Executando ação personalizada...',
                    action: 'MINHA_ACAO'
                },
            },
        ],
    ] as ActionExample[][],

    validate: async (runtime: IAgentRuntime, message: Memory, state?: State) => {
        // Lógica de validação
        return true;
    },

    handler: async (runtime: IAgentRuntime, message: Memory, state?: State) => {
        // Lógica da ação
        console.log('Executando ação personalizada');

        // Realizar operações
        const resultado = await realizarOperacao();

        return {
            text: `Ação executada com sucesso: ${resultado}`,
            success: true,
        };
    },
};
```

#### Exemplo de Serviço:

```typescript
// src/services/meu-servico.ts
import { Service, IAgentRuntime } from '@elizaos/core';

export class MeuServico extends Service {
    static serviceType = 'MEU_SERVICO';

    constructor() {
        super();
    }

    async initialize(runtime: IAgentRuntime): Promise<void> {
        console.log('Inicializando MeuServico...');
        // Configuração inicial
    }

    async processar(dados: any): Promise<any> {
        // Lógica de processamento
        return { processado: true, dados };
    }
}
```

### Construir o Plugin

Construa o plugin usando o seguinte comando:

```bash
pnpm build --filter ./packages/plugin-foo

# Ou construa todos os pacotes
pnpm build
```

### Adicionar Plugin ao character.json

Digamos que você quer adicionar o plugin ao personagem sample que está em `characters/sample.character.json`:

```json
{
    "name": "Sample",
    "plugins": [
        "@elizaos-plugins/plugin-foo"
    ]
}
```

⚠️ **Aviso:** Se você está usando Injeção de Dependência (@elizaos-plugins/plugin-di) em seu plugin, lembre-se de adicioná-lo ao campo `postProcessors`. E o campo `clients` está depreciado na versão mais recente do Eliza, então se você quiser adicionar clientes, também precisa usar o campo `plugins`.

```json
{
    "name": "Sample",
    "plugins": [
        "@elizaos-plugins/plugin-foo",
        "@elizaos-plugins/client-discord"
    ],
    "postProcessors": [
        "@elizaos-plugins/plugin-di"
    ]
}
```

### Executar o Agente Eliza com seu Plugin

Execute o agente Eliza para testar o plugin:

```bash
pnpm start --character="characters/sample.character.json"

# Ou com mais logs de debug
pnpm start:debug --character="characters/sample.character.json"
```

## Desenvolvimento Avançado de Plugins

### Usando Injeção de Dependência

Se você escolher usar injeção de dependência, sua estrutura ficará assim:

```typescript
// src/actions/minha-acao-di.ts
import { Injectable } from '@elizaos-plugins/plugin-di';
import { Action, IAgentRuntime, Memory } from '@elizaos/core';

@Injectable()
export class MinhaAcaoDI implements Action {
    name = 'MINHA_ACAO_DI';
    description = 'Ação com injeção de dependência';

    constructor(private meuServico: MeuServico) {}

    async handler(runtime: IAgentRuntime, message: Memory) {
        const resultado = await this.meuServico.processar(message);
        return { text: `Resultado: ${resultado}` };
    }
}
```

### Integração com Flow Blockchain

Exemplo de plugin que interage com Flow:

```typescript
// src/actions/flow-balance.ts
import { Action, IAgentRuntime, Memory } from '@elizaos/core';
import * as fcl from '@onflow/fcl';

export const FlowBalance: Action = {
    name: 'FLOW_BALANCE',
    description: 'Verifica o saldo de FLOW de uma conta',

    handler: async (runtime: IAgentRuntime, message: Memory) => {
        const address = extractAddress(message.content.text);

        fcl.config({
            'accessNode.api': 'https://rest-testnet.onflow.org',
        });

        const account = await fcl.account(address);
        const balance = account.balance / 100000000; // Converter de UFix64

        return {
            text: `O saldo da conta ${address} é ${balance} FLOW`,
        };
    },
};
```

## Interagir com o Agente

Agora você está pronto para iniciar uma conversa com seu agente.

Abra uma nova janela de terminal e execute o servidor http do cliente:

```bash
pnpm start:client
```

## Registro de Plugin

Você precisa registrar seu plugin no [Registro de Plugins Eliza](https://github.com/elizaos/plugin-registry) para torná-lo disponível para outros usuários.

Por favor, siga o guia lá, modifique o `index.json` e envie um PR para o repositório do registro.

### Estrutura do Registro:

```json
{
    "name": "@elizaos-plugins/plugin-foo",
    "description": "Plugin personalizado para funcionalidades foo",
    "version": "1.0.0",
    "author": "Seu Nome",
    "repository": "https://github.com/username/plugin-foo",
    "keywords": ["foo", "custom", "flow"],
    "category": "utility"
}
```

## Melhores Práticas

1. **Modularidade:** Mantenha plugins focados em uma funcionalidade específica
2. **Documentação:** Sempre documente suas ações, serviços e configurações
3. **Testes:** Inclua testes unitários para suas ações e serviços
4. **Versionamento:** Use versionamento semântico para seu plugin
5. **Exemplos:** Forneça exemplos claros de uso em seu README

## Conclusão

Neste tutorial, você aprendeu como desenvolver plugins personalizados para Eliza. Você ganhou experiência com criação de repositórios de plugins, implementação de ações e serviços personalizados, integração de plugins com agentes, e uso de injeção de dependência para melhor arquitetura.

O sistema de plugins do Eliza fornece uma maneira poderosa de estender a funcionalidade de seus agentes de IA. Com o conhecimento adquirido neste tutorial, você pode agora desenvolver plugins mais sofisticados, criar componentes reutilizáveis e compartilhar seu trabalho através do registro de plugins.

---

*Este material faz parte do Bootcamp de AI Agents no Flow Blockchain*