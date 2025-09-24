# Usar Flow MCP no Cursor

Adicionar Flow MCP ao Cursor oferece ferramentas poderosas orientadas por IA diretamente dentro do seu editor de código. Isso permite que a IA do Cursor entenda, consulte e interaja com dados do blockchain Flow e smart contracts através de um protocolo padrão chamado Model Context Protocol (MCP).

Especificamente, ele permite que você:

- Peça à IA no Cursor para buscar dados onchain como saldos de contas, informações de contas ou código fonte de contratos sem sair do seu editor
- Acelere o desenvolvimento permitindo que a IA realize consultas blockchain que normalmente exigiriam etapas manuais
- Melhore o contexto para assistência de IA permitindo que o Cursor puxe dados reais do blockchain quando necessário
- Automatize tarefas rotineiras do Flow usando ferramentas expostas pelo servidor MCP
- Prototipe e depure mais rapidamente com acesso direto a informações blockchain ao vivo

Este tutorial irá guiá-lo através da configuração e uso do Flow MCP no Cursor para aprimorar sua experiência de desenvolvimento blockchain Flow com assistência de IA.

## Objetivos de Aprendizagem

Após completar este tutorial, você deve ser capaz de:

- Configurar o Cursor para conectar com o servidor Flow MCP usando o protocolo MCP
- Instalar e iniciar o servidor Flow MCP localmente através do Cursor
- Identificar quando as ferramentas Flow MCP estão carregadas com sucesso e prontas dentro do Cursor
- Usar ferramentas Flow MCP para recuperar dados blockchain como saldos de contas, detalhes de contas e código fonte de contratos
- Solucionar problemas comuns de configuração e conectividade entre Cursor e Flow MCP

## Pré-requisitos

- **Cursor** - o editor de código com IA
- **Flow MCP GitHub Repository** - o repositório do servidor Flow MCP

## Instalação

### 1. Abrir Configurações do Cursor

Abra as Configurações do Cursor e vá para a aba "MCP".

![Configurações do Cursor](./images/cursor-settings.png)

### 2. Configurar o arquivo de configuração MCP

O arquivo de configuração MCP está localizado no seguinte local baseado no seu sistema operacional:

- **macOS:** `~/Library/Application Support/Cursor/mcp.json`
- **Windows:** `%APPDATA%/Cursor/mcp.json`
- **Linux:** `~/.config/Cursor/mcp.json`

### 3. Adicionar a configuração do Flow MCP

Adicione a seguinte configuração ao arquivo `mcp.json`:

```json
{
  "mcpServers": {
    "flow-mcp": {
      "command": "npx",
      "args": ["-y", "@outblock/flow-mcp"]
    }
  }
}
```

### 4. Reiniciar o Cursor

Reinicie o Cursor para carregar a nova configuração MCP.

### 5. Verificar se o servidor está pronto

Você precisa aguardar o servidor MCP iniciar. Uma vez pronto, você verá:
- Um ponto verde ao lado do nome do servidor "flow-mcp"
- Todas as ferramentas do Flow MCP serão exibidas

![Flow MCP servidor pronto](./images/flow-mcp-ready.png)

## Como usar Flow MCP no Cursor

### Verificando Saldo de FLOW

Exemplo de como verificar o saldo de uma conta:

```
Pergunta: "Qual é o saldo de FLOW da conta 0x1234567890abcdef?"

Resposta da IA: "Vou verificar o saldo dessa conta no Flow..."
[Usa ferramenta: getBalance]
"O saldo da conta 0x1234567890abcdef é 100.5 FLOW"
```

### Visualizando Informações da Conta

Exemplo de como obter informações detalhadas de uma conta:

```
Pergunta: "Mostre-me as informações da conta 0xf8d6e0586b0a20c7"

Resposta da IA: "Vou buscar as informações dessa conta..."
[Usa ferramenta: getAccount]
"Aqui estão as informações da conta:
- Endereço: 0xf8d6e0586b0a20c7
- Saldo: 50.25 FLOW
- Número de chaves: 2
- Contratos implantados: 3
- Código de armazenamento usado: 1024 bytes"
```

### Obtendo Código Fonte de Contrato

Exemplo de como recuperar o código de um smart contract:

```
Pergunta: "Mostre o código do contrato FungibleToken na conta 0x9a0766d93b6608b7"

Resposta da IA: "Vou buscar o código fonte desse contrato..."
[Usa ferramenta: getContract]
"Aqui está o código do contrato FungibleToken:
```cadence
pub contract FungibleToken {
    pub resource interface Provider {
        pub fun withdraw(amount: UFix64): @Vault
    }
    // ... resto do código
}
```"
```

## Exemplos Práticos

### 1. Desenvolvimento de Smart Contract

```
Você: "Preciso ver o contrato NonFungibleToken no mainnet e entender sua estrutura"

IA: "Vou buscar o contrato NonFungibleToken do mainnet para você analisar..."
[Busca e exibe o contrato com explicações]
```

### 2. Depuração de Transações

```
Você: "Verifique se a conta 0x123 tem saldo suficiente para executar uma transação de 10 FLOW"

IA: "Verificando o saldo da conta..."
[Verifica saldo e analisa viabilidade]
```

### 3. Análise de Conta

```
Você: "Analise a conta 0xabc e me diga que contratos ela tem implantados"

IA: "Analisando a conta especificada..."
[Lista contratos e fornece detalhes]
```

## Configuração Avançada

### Configurar para Rede Específica

```json
{
  "mcpServers": {
    "flow-mcp-testnet": {
      "command": "npx",
      "args": ["-y", "@outblock/flow-mcp"],
      "env": {
        "FLOW_NETWORK": "testnet"
      }
    },
    "flow-mcp-mainnet": {
      "command": "npx",
      "args": ["-y", "@outblock/flow-mcp"],
      "env": {
        "FLOW_NETWORK": "mainnet"
      }
    }
  }
}
```

### Habilitar Logs de Debug

```json
{
  "mcpServers": {
    "flow-mcp": {
      "command": "npx",
      "args": ["-y", "@outblock/flow-mcp"],
      "env": {
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

## Solução de Problemas

### Servidor não inicia

Se o servidor MCP não iniciar:

1. **Verifique a instalação do Node.js**
   ```bash
   node --version  # Deve ser 18+
   npm --version   # Deve ser 8+
   ```

2. **Verifique o arquivo de configuração**
   - Certifique-se de que o JSON está válido
   - Verifique o caminho correto do arquivo

3. **Limpe o cache do npm**
   ```bash
   npm cache clean --force
   ```

### Ferramentas não aparecem

Se as ferramentas não aparecem no Cursor:

1. **Reinicie completamente o Cursor**
   - Feche todas as janelas
   - Reinicie o aplicativo

2. **Verifique o status do servidor**
   - Procure pelo ponto verde ao lado do nome do servidor
   - Verifique o console para mensagens de erro

3. **Teste manualmente o servidor**
   ```bash
   npx -y @outblock/flow-mcp
   ```

### Erro de conexão com Flow

Se houver erros ao conectar com o blockchain Flow:

1. **Verifique a conectividade de rede**
   ```bash
   ping rest-testnet.onflow.org
   ```

2. **Teste o access node**
   ```bash
   curl https://rest-testnet.onflow.org/v1/blocks?height=sealed
   ```

3. **Configure um access node alternativo**
   ```json
   {
     "env": {
       "FLOW_ACCESS_NODE": "https://rest-mainnet.onflow.org"
     }
   }
   ```

## Melhores Práticas

### 1. Use Contexto Específico

Seja específico em suas perguntas para obter melhores resultados:
- ✅ "Qual o saldo de FLOW da conta 0x123 na testnet?"
- ❌ "Qual o saldo?"

### 2. Combine Ferramentas

Use múltiplas ferramentas em sequência:
```
"Primeiro verifique o saldo da conta 0x123, depois mostre os contratos implantados nela"
```

### 3. Valide Resultados

Sempre valide informações críticas:
```
"Verifique duas vezes o saldo antes de executar a transação"
```

### 4. Use para Aprendizado

Aprenda sobre contratos existentes:
```
"Analise o contrato FlowToken e explique suas principais funções"
```

## Recursos Adicionais

- [Flow MCP GitHub](https://github.com/outblock/flow-mcp)
- [Documentação do Cursor](https://cursor.sh/docs)
- [Flow Developer Portal](https://developers.flow.com)
- [Model Context Protocol Spec](https://modelcontextprotocol.io)

## Conclusão

O Flow MCP no Cursor transforma sua experiência de desenvolvimento blockchain, trazendo dados e operações do Flow diretamente para seu ambiente de codificação assistido por IA. Com esta integração, você pode:

- Desenvolver mais rapidamente com acesso instantâneo a dados blockchain
- Depurar problemas com informações ao vivo
- Aprender explorando contratos e contas reais
- Automatizar tarefas repetitivas

Continue explorando as capacidades do Flow MCP e considere contribuir com novas ferramentas para expandir o ecossistema!

---

*Este material faz parte do Bootcamp de AI Agents no Flow Blockchain*