# 🎯 Exercício 1: Hello Flow

## 📊 Informações
- **Pontos**: 5
- **Dificuldade**: Iniciante
- **Tempo estimado**: 30 minutos
- **Pré-requisito**: Flow CLI instalado

## 🎯 Objetivo
Criar seu primeiro smart contract em Cadence e fazer deploy no emulador local.

## 📝 Instruções

### Passo 1: Setup do Projeto
```bash
# Criar diretório do projeto
mkdir hello-flow
cd hello-flow

# Inicializar projeto Flow
flow init

# Iniciar emulador em um terminal
flow emulator start
```

### Passo 2: Criar o Contrato
Crie o arquivo `contracts/HelloWorld.cdc`:

```cadence
pub contract HelloWorld {

    // Variável de estado para armazenar a mensagem
    pub var greeting: String

    // Evento emitido quando a mensagem muda
    pub event GreetingChanged(oldGreeting: String, newGreeting: String)

    // Função para ler a mensagem
    pub fun getGreeting(): String {
        return self.greeting
    }

    // Função para atualizar a mensagem
    pub fun setGreeting(newGreeting: String) {
        let oldGreeting = self.greeting
        self.greeting = newGreeting
        emit GreetingChanged(oldGreeting: oldGreeting, newGreeting: newGreeting)
    }

    // Inicializador do contrato
    init() {
        self.greeting = "Hello, Flow Blockchain!"
    }
}
```

### Passo 3: Configurar flow.json
Adicione ao `flow.json`:

```json
{
  "contracts": {
    "HelloWorld": "./contracts/HelloWorld.cdc"
  },
  "deployments": {
    "emulator": {
      "emulator-account": ["HelloWorld"]
    }
  }
}
```

### Passo 4: Deploy do Contrato
```bash
# Em outro terminal (com emulador rodando)
flow project deploy
```

### Passo 5: Criar Script de Leitura
Crie `scripts/GetGreeting.cdc`:

```cadence
import HelloWorld from 0xf8d6e0586b0a20c7

pub fun main(): String {
    return HelloWorld.getGreeting()
}
```

### Passo 6: Executar o Script
```bash
flow scripts execute scripts/GetGreeting.cdc
```

### Passo 7: Criar Transação de Atualização
Crie `transactions/SetGreeting.cdc`:

```cadence
import HelloWorld from 0xf8d6e0586b0a20c7

transaction(newGreeting: String) {
    prepare(signer: AuthAccount) {
        // Não precisa de preparação especial
    }

    execute {
        HelloWorld.setGreeting(newGreeting: newGreeting)
    }
}
```

### Passo 8: Executar a Transação
```bash
flow transactions send transactions/SetGreeting.cdc "Hello, Diego!"
```

## ✅ Critérios de Sucesso
- [ ] Contrato deployado com sucesso
- [ ] Script retorna mensagem inicial
- [ ] Transação atualiza mensagem
- [ ] Eventos são emitidos corretamente
- [ ] Novo script retorna mensagem atualizada

## 🎁 Bônus (+2 pontos)
Adicione uma funcionalidade extra:

1. **Contador de atualizações**: Adicione uma variável que conta quantas vezes a mensagem foi atualizada
2. **Histórico**: Mantenha um array com as últimas 5 mensagens
3. **Timestamp**: Adicione timestamp da última atualização

## 💡 Dicas
- Use `flow emulator --verbose` para ver logs detalhados
- O endereço `0xf8d6e0586b0a20c7` é a conta padrão do emulador
- Eventos podem ser vistos nos logs do emulador
- Use `flow accounts get 0xf8d6e0586b0a20c7` para ver detalhes da conta

## 🐛 Troubleshooting

### Erro: "Cannot find contract"
- Verifique se o contrato foi deployado: `flow project deploy`
- Confirme o endereço correto no script

### Erro: "Transaction failed"
- Certifique-se que o emulador está rodando
- Verifique a sintaxe do Cadence

### Erro: "Invalid import"
- O endereço no import deve corresponder ao deploy

## 📚 Recursos
- [Cadence Playground](https://play.flow.com)
- [Documentação Cadence](https://developers.flow.com/cadence)
- [Flow CLI Reference](https://developers.flow.com/tools/flow-cli)

## 🏆 Submissão
Quando completar o exercício:

1. Tire screenshot do output dos comandos
2. Salve em `exercicios/fase1/01_hello_flow_completo.png`
3. Atualize seu score: +5 pontos base, +2 se fez bônus

---

**Próximo exercício**: [02_resources_basics.md](./02_resources_basics.md) (desbloqueado após completar este)