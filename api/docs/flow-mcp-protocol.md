# Flow MCP (Model Context Protocol)

O Model Context Protocol (MCP) é um padrão aberto que permite que aplicações de IA interajam perfeitamente com ferramentas, sistemas e fontes de dados externos. O Flow MCP estende este protocolo para fornecer às ferramentas de IA acesso direto aos dados do blockchain Flow, smart contracts e operações onchain. Esta integração permite que desenvolvedores aprimorem seus fluxos de trabalho de desenvolvimento alimentados por IA com informações blockchain em tempo real e interações automatizadas com Flow.

O Flow MCP transforma como os desenvolvedores trabalham com o blockchain Flow, trazendo capacidades blockchain diretamente para editores de código e ferramentas de desenvolvimento alimentados por IA, eliminando a necessidade de alternar entre diferentes interfaces e permitindo experiências de desenvolvimento mais eficientes e conscientes do contexto.

## Usar Flow MCP no Cursor

Aprenda como integrar o servidor Flow MCP com Cursor para habilitar consultas blockchain orientadas por IA diretamente dentro do seu editor de código. Este tutorial guia você através da configuração do Flow MCP no Cursor, permitindo que a IA busque dados onchain como saldos de conta, informações de contrato e estado do blockchain sem sair do seu ambiente de desenvolvimento. Ao final deste tutorial, você será capaz de pedir à IA do Cursor para realizar operações blockchain Flow, acelerar fluxos de trabalho de desenvolvimento e acessar dados blockchain ao vivo para depuração e prototipagem aprimoradas.

## Contribuir para Flow MCP

Descubra como estender o servidor Flow MCP criando Action Tools personalizadas que adicionam novas capacidades de interação blockchain. Este guia abrangente orienta você através do processo de desenvolvimento, desde a configuração do ambiente de desenvolvimento até o envio de pull requests para novos recursos. Aprenda a criar novas ferramentas com schemas, handlers e testes adequados, seguindo as diretrizes de contribuição do Flow MCP. Este tutorial capacita desenvolvedores a expandir o ecossistema Flow MCP adicionando ferramentas blockchain especializadas que beneficiam toda a comunidade de desenvolvedores Flow.

## Benefícios do Flow MCP

### Integração Nativa com IA
- Acesso direto a dados blockchain através de ferramentas de IA
- Consultas contextuais sem sair do editor
- Automação de tarefas repetitivas

### Desenvolvimento Acelerado
- Eliminação de trocas de contexto entre ferramentas
- Acesso instantâneo a informações blockchain
- Depuração mais eficiente com dados ao vivo

### Extensibilidade
- Sistema de plugins para adicionar novas funcionalidades
- Padrão aberto para integração com múltiplas ferramentas
- Contribuições da comunidade para expandir capacidades

## Casos de Uso

### Desenvolvimento de Smart Contracts
- Visualizar código de contratos diretamente no editor
- Verificar estado de contratos em tempo real
- Testar interações sem sair do ambiente de desenvolvimento

### Análise de Dados Onchain
- Consultar saldos e informações de contas
- Monitorar transações e eventos
- Analisar métricas blockchain

### Automação de Tarefas
- Deploy automatizado de contratos
- Execução de scripts de teste
- Gestão de contas e chaves

## Arquitetura do Flow MCP

### Componentes Principais

1. **Servidor MCP**
   - Gerencia conexões com ferramentas de IA
   - Processa requisições e respostas
   - Mantém estado da sessão

2. **Action Tools**
   - Implementam funcionalidades específicas
   - Definem schemas de entrada/saída
   - Executam operações blockchain

3. **Protocolo de Comunicação**
   - Baseado em JSON-RPC
   - Suporta streaming de dados
   - Tratamento de erros padronizado

### Fluxo de Dados

```
Editor de IA (Cursor) <-> Servidor MCP <-> Flow Blockchain
         ^                      ^                  ^
         |                      |                  |
    Requisições            Processamento      Operações
      do Usuário            de Comandos        Onchain
```

## Ferramentas Disponíveis

### Consultas de Conta
- `getAccount`: Obter informações detalhadas de uma conta
- `getBalance`: Verificar saldo de FLOW
- `getKeys`: Listar chaves de uma conta

### Contratos
- `getContract`: Buscar código fonte de um contrato
- `getContractEvents`: Consultar eventos de contrato
- `deployContract`: Deploy de novo contrato

### Transações
- `sendTransaction`: Enviar transação personalizada
- `getTransaction`: Consultar status de transação
- `getTransactionResult`: Obter resultado de transação

## Configuração Avançada

### Variáveis de Ambiente

```env
FLOW_NETWORK=testnet          # ou mainnet
FLOW_ACCESS_NODE=https://rest-testnet.onflow.org
FLOW_PRIVATE_KEY=xxx          # Para operações que requerem assinatura
```

### Configuração Personalizada

```json
{
  "mcpServers": {
    "flow-mcp": {
      "command": "npx",
      "args": ["-y", "@outblock/flow-mcp"],
      "env": {
        "FLOW_NETWORK": "testnet",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

## Segurança

### Melhores Práticas

1. **Nunca exponha chaves privadas** em configurações compartilhadas
2. **Use testnet** para desenvolvimento e testes
3. **Valide entrada** antes de executar operações
4. **Implemente rate limiting** para prevenir abuso
5. **Audite logs** regularmente

### Considerações de Segurança

- MCP roda localmente por padrão
- Comunicação criptografada quando configurada
- Isolamento de contexto entre sessões
- Permissões granulares para operações

## Roadmap

### Funcionalidades Planejadas

- Suporte para Cadence 1.0
- Integração com Flow Wallet API
- Análise de gas e otimização
- Templates de contratos inteligentes
- Debugging visual de transações

### Contribuições da Comunidade

O Flow MCP é um projeto open source e aceita contribuições:

- Novas Action Tools
- Melhorias de performance
- Documentação e tutoriais
- Correções de bugs
- Testes e validação

## Conclusão

O Flow MCP faz a ponte entre ferramentas de desenvolvimento de IA e funcionalidade blockchain, permitindo que desenvolvedores acessem os recursos abrangentes do blockchain Flow diretamente através de interfaces alimentadas por IA. Seja usando ferramentas MCP existentes no Cursor ou contribuindo com novas capacidades para o servidor Flow MCP, estes tutoriais fornecem a base para integrar operações blockchain em seu fluxo de trabalho de desenvolvimento aprimorado por IA.

---

*Este material faz parte do Bootcamp de AI Agents no Flow Blockchain*