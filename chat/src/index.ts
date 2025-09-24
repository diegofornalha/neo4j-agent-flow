/**
 * Flow Native Bootcamp - 100% Flow Blockchain
 * Sem ElizaOS - Agentes nativos puros
 */

import * as fcl from '@onflow/fcl';
import * as types from '@onflow/types';
import dotenv from 'dotenv';

// Carregar configurações
dotenv.config();

// Configuração Flow
fcl.config({
  "accessNode.api": process.env.FLOW_ACCESS_NODE || "https://rest-testnet.onflow.org",
  "discovery.wallet": "https://fcl-discovery.onflow.org/testnet/authn",
});

/**
 * Flow Native Agent - Simples e Direto
 */
class FlowNativeAgent {
  private accountAddress: string;
  private privateKey: string;

  constructor() {
    this.accountAddress = process.env.FLOW_ACCOUNT_ADDRESS || '';
    this.privateKey = process.env.FLOW_PRIVATE_KEY || '';

    console.log('🌊 Flow Native Agent - Bootcamp Simplificado');
    console.log('✨ 100% Flow Blockchain - Sem frameworks externos');
    console.log('=' . repeat(50));
  }

  /**
   * Inicializar agente
   */
  async initialize() {
    console.log('🚀 Inicializando Flow Native Agent...');

    try {
      // Verificar conta Flow
      const account = await fcl.account(this.accountAddress);
      console.log(`✅ Conta conectada: ${account.address}`);
      console.log(`💰 Saldo: ${(account.balance / 100000000).toFixed(2)} FLOW`);

      // Listar contratos
      const contracts = Object.keys(account.contracts);
      if (contracts.length > 0) {
        console.log('📜 Contratos deployados:');
        contracts.forEach(name => {
          console.log(`   • ${name}`);
        });
      }

      console.log('✅ Agent pronto para operar!');
      console.log('');

    } catch (error) {
      console.error('❌ Erro ao conectar:', error);
      throw error;
    }
  }

  /**
   * Transferir FLOW tokens
   */
  async transferFlow(to: string, amount: number) {
    console.log(`💸 Transferindo ${amount} FLOW para ${to}...`);

    const cadence = `
      import FlowToken from 0x1654653399040a61
      import FungibleToken from 0xf233dcee88fe0abe

      transaction(amount: UFix64, to: Address) {
        let sentVault: @FungibleToken.Vault

        prepare(signer: AuthAccount) {
          let vaultRef = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Could not borrow reference to the owner's Vault!")

          self.sentVault <- vaultRef.withdraw(amount: amount)
        }

        execute {
          let recipient = getAccount(to)
          let receiverRef = recipient.getCapability(/public/flowTokenReceiver)
            .borrow<&{FungibleToken.Receiver}>()
            ?? panic("Could not borrow receiver reference")

          receiverRef.deposit(from: <-self.sentVault)
        }
      }
    `;

    try {
      const txid = await fcl.mutate({
        cadence,
        args: (arg: any, t: any) => [
          arg(amount.toFixed(8), t.UFix64),
          arg(to, t.Address)
        ],
        proposer: fcl.authz,
        payer: fcl.authz,
        authorizations: [fcl.authz],
        limit: 100
      });

      console.log(`✅ Transação enviada: ${txid}`);

      const tx = await fcl.tx(txid).onceSealed();
      console.log(`✅ Confirmada no bloco: ${tx.blockId}`);

      return tx;

    } catch (error) {
      console.error('❌ Erro na transferência:', error);
      throw error;
    }
  }

  /**
   * Ler saldo de conta
   */
  async getBalance(address?: string) {
    const target = address || this.accountAddress;

    const account = await fcl.account(target);
    const balance = account.balance / 100000000;

    console.log(`💰 Saldo de ${target}: ${balance.toFixed(2)} FLOW`);
    return balance;
  }

  /**
   * Executar script Cadence
   */
  async executeScript(code: string, args: any[] = []) {
    console.log('📝 Executando script Cadence...');

    try {
      const result = await fcl.query({
        cadence: code,
        args: (arg: any, t: any) => args
      });

      console.log('✅ Resultado:', result);
      return result;

    } catch (error) {
      console.error('❌ Erro no script:', error);
      throw error;
    }
  }

  /**
   * Monitorar eventos
   */
  async monitorEvents(eventType: string) {
    console.log(`👁️ Monitorando eventos: ${eventType}`);

    // Subscribe para eventos
    const unsub = fcl.events(eventType).subscribe((event: any) => {
      console.log('📡 Evento recebido:');
      console.log(`   Tipo: ${event.type}`);
      console.log(`   Bloco: ${event.blockId}`);
      console.log(`   Dados:`, event.data);
    });

    return unsub;
  }

  /**
   * Deploy de contrato
   */
  async deployContract(name: string, code: string) {
    console.log(`📜 Deployando contrato ${name}...`);

    const txCode = `
      transaction(name: String, code: String) {
        prepare(signer: AuthAccount) {
          signer.contracts.add(
            name: name,
            code: code.decodeHex()
          )
        }
      }
    `;

    try {
      const hexCode = Buffer.from(code).toString('hex');

      const txid = await fcl.mutate({
        cadence: txCode,
        args: (arg: any, t: any) => [
          arg(name, t.String),
          arg(hexCode, t.String)
        ],
        proposer: fcl.authz,
        payer: fcl.authz,
        authorizations: [fcl.authz],
        limit: 1000
      });

      console.log(`✅ Deploy enviado: ${txid}`);

      const tx = await fcl.tx(txid).onceSealed();
      console.log(`✅ Contrato ${name} deployado!`);

      return tx;

    } catch (error) {
      console.error('❌ Erro no deploy:', error);
      throw error;
    }
  }
}

// ========================================
// EXEMPLOS DE USO
// ========================================

async function demonstrarCapacidades() {
  console.log('🎯 DEMONSTRAÇÃO FLOW NATIVE BOOTCAMP');
  console.log('=' . repeat(50));
  console.log('');

  const agent = new FlowNativeAgent();
  await agent.initialize();

  // Exemplos de operações
  console.log('📚 OPERAÇÕES DISPONÍVEIS:');
  console.log('');
  console.log('1️⃣ Transferência de FLOW:');
  console.log('   await agent.transferFlow("0x123...", 10.0);');
  console.log('');
  console.log('2️⃣ Consultar Saldo:');
  console.log('   await agent.getBalance("0x123...");');
  console.log('');
  console.log('3️⃣ Executar Script:');
  console.log('   await agent.executeScript(cadenceCode);');
  console.log('');
  console.log('4️⃣ Monitorar Eventos:');
  console.log('   await agent.monitorEvents("A.0x1.FlowToken.TokensDeposited");');
  console.log('');
  console.log('5️⃣ Deploy de Contratos:');
  console.log('   await agent.deployContract("MyContract", code);');
  console.log('');

  // Verificar saldo atual
  await agent.getBalance();

  // Monitorar eventos de depósito
  const eventType = "A.0x1654653399040a61.FlowToken.TokensDeposited";
  console.log(`\n📡 Monitorando eventos ${eventType.split('.').pop()}...`);
  console.log('   (Pressione Ctrl+C para parar)');

  const unsub = await agent.monitorEvents(eventType);

  // Manter rodando
  process.on('SIGINT', () => {
    console.log('\n👋 Encerrando Flow Native Bootcamp...');
    unsub();
    process.exit(0);
  });
}

// ========================================
// VANTAGENS DO FLOW NATIVE
// ========================================

function mostrarVantagens() {
  console.log('');
  console.log('💎 VANTAGENS DO FLOW NATIVE:');
  console.log('');
  console.log('✅ Simplicidade:');
  console.log('   • Sem frameworks complexos');
  console.log('   • Direto com FCL e Cadence');
  console.log('   • Código limpo e manutenível');
  console.log('');
  console.log('⚡ Performance:');
  console.log('   • 800ms block time');
  console.log('   • $0.000179 custo médio');
  console.log('   • Sub-second finality');
  console.log('');
  console.log('🛡️ Segurança:');
  console.log('   • Resource-oriented programming');
  console.log('   • Capability-based access');
  console.log('   • Sem riscos de reentrância');
  console.log('');
  console.log('🚀 Escalabilidade:');
  console.log('   • 1M TPS target');
  console.log('   • Multi-role architecture');
  console.log('   • Sem sharding necessário');
  console.log('');
}

// ========================================
// MAIN
// ========================================

async function main() {
  try {
    await demonstrarCapacidades();
    mostrarVantagens();
  } catch (error) {
    console.error('❌ Erro:', error);
    process.exit(1);
  }
}

// Executar
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { FlowNativeAgent };
export default FlowNativeAgent;