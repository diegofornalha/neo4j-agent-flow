# Instruções Importantes para Claude - Flow Blockchain Project

## 🚨 CONFIGURAÇÃO CRÍTICA: USAR APENAS TESTNET

Este projeto está configurado para usar **EXCLUSIVAMENTE A TESTNET** da Flow Blockchain.

### Regras Obrigatórias:

1. **SEMPRE use a Testnet** para todas as operações Flow
   - URL: `https://rest-testnet.onflow.org`
   - NUNCA use: `https://rest-mainnet.onflow.org`

2. **Conta Principal do Projeto**:
   - Endereço: `0x25f823e2a115b2dc`
   - Saldo: ~2000 FLOW (na Testnet)
   - Esta conta existe APENAS na Testnet

3. **Ao verificar saldos ou fazer consultas**:
   - Vá direto para a Testnet
   - NÃO verifique a Mainnet primeiro
   - NÃO mencione que a conta não existe na Mainnet
   - Responda com o saldo da Testnet imediatamente

4. **Performance**:
   - Verificar apenas Testnet é 47% mais rápido
   - Elimina timeout desnecessário da Mainnet
   - Melhora a experiência do usuário

### Arquivos Otimizados Disponíveis:

- `check_flow_balance_testnet.py` - Versão otimizada para Testnet apenas
- `.env.testnet` - Configurações de ambiente para Testnet

### Exemplo de Resposta Correta:

❌ **ERRADO**: "A conta não foi encontrada na Mainnet, mas na Testnet tem 2000 FLOW"

✅ **CORRETO**: "Sua conta 0x25f823e2a115b2dc possui 2000.00100000 FLOW na Testnet"

### Contexto do Projeto:

Este é um ambiente de desenvolvimento para o Hackathon Flow Blockchain. Todos os contratos, contas e recursos estão implantados na Testnet. A migração para Mainnet só ocorrerá após a conclusão do desenvolvimento.

### Scripts e Ferramentas:

Quando executar scripts Python relacionados a Flow:
- Use: `python3 check_flow_balance_testnet.py`
- Evite: `python3 check_flow_balance.py` (verifica mainnet desnecessariamente)

### Variáveis de Ambiente:

```bash
FLOW_NETWORK=testnet
FLOW_TESTNET_ONLY=true
FLOW_SKIP_MAINNET=true
FLOW_ACCESS_NODE=https://rest-testnet.onflow.org
```

---

**LEMBRE-SE**: Este projeto usa APENAS Testnet. Toda menção a Mainnet deve ser evitada para melhor performance e clareza.