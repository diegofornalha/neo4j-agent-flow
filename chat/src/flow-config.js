import * as fcl from "@onflow/fcl";

// Endereços importantes na testnet
const CONTRACT_ADDRESSES = {
  FlowToken: "0x7e60df042a9c0868",
  FungibleToken: "0x9a0766d93b6608b7",
  NonFungibleToken: "0x631e88ae7f1d7c20",
  MetadataViews: "0x631e88ae7f1d7c20",

  // Nossos contratos (quando fizer deploy)
  QuizRace: "0x01cf0e2f2f715450",
  QuizPassNFT: "0x01cf0e2f2f715450",
  FlowAgentActions: "0x01cf0e2f2f715450"
};

// Configuração do FCL
fcl.config()
  // Rede
  .put("flow.network", "testnet")
  .put("accessNode.api", "https://rest-testnet.onflow.org")

  // Wallet Discovery (permite conectar wallets)
  .put("discovery.wallet", "https://fcl-discovery.onflow.org/testnet/authn")
  .put("discovery.authn.endpoint", "https://fcl-discovery.onflow.org/api/testnet/authn")

  // Metadata do App (aparece na wallet)
  .put("app.detail.title", "Flow Native Agents - Bootcamp")
  .put("app.detail.icon", "https://flow.com/favicon.ico")
  .put("app.detail.description", "Sistema de agentes autônomos nativos com quiz educacional sobre Flow")
  .put("app.detail.url", "https://github.com/neo4j-agent-flow")

  // Contratos
  .put("0xFlowToken", CONTRACT_ADDRESSES.FlowToken)
  .put("0xFungibleToken", CONTRACT_ADDRESSES.FungibleToken)
  .put("0xNonFungibleToken", CONTRACT_ADDRESSES.NonFungibleToken)
  .put("0xQuizRace", CONTRACT_ADDRESSES.QuizRace);

// Exporta FCL configurado
export { fcl };

// ========== FUNÇÕES ÚTEIS ==========

/**
 * Conecta wallet do usuário
 */
export async function connectWallet() {
  try {
    await fcl.authenticate();
    const user = await fcl.currentUser.snapshot();
    return user;
  } catch (error) {
    console.error("Erro ao conectar wallet:", error);
    throw error;
  }
}

/**
 * Desconecta wallet
 */
export async function disconnectWallet() {
  await fcl.unauthenticate();
}

/**
 * Obtém informações da conta
 */
export async function getAccount(address) {
  try {
    const account = await fcl.account(address);
    return {
      address: account.address,
      balance: account.balance,
      keys: account.keys.filter(k => !k.revoked),
      contracts: Object.keys(account.contracts)
    };
  } catch (error) {
    console.error("Erro ao buscar conta:", error);
    return null;
  }
}

/**
 * Obtém saldo de FLOW
 */
export async function getFlowBalance(address) {
  const account = await getAccount(address);
  return account ? parseFloat(account.balance) / 100000000 : 0;
}

/**
 * Executa script Cadence
 */
export async function executeScript(cadence, args = []) {
  try {
    const response = await fcl.query({
      cadence,
      args: (arg, t) => args
    });
    return response;
  } catch (error) {
    console.error("Erro ao executar script:", error);
    throw error;
  }
}

/**
 * Envia transação
 */
export async function sendTransaction(cadence, args = [], options = {}) {
  try {
    const transactionId = await fcl.mutate({
      cadence,
      args: (arg, t) => args,
      proposer: fcl.currentUser,
      payer: fcl.currentUser,
      authorizations: [fcl.currentUser],
      limit: options.limit || 100,
      ...options
    });

    // Aguarda execução
    const transaction = await fcl.tx(transactionId).onceSealed();
    return {
      transactionId,
      status: transaction.status,
      events: transaction.events,
      error: transaction.errorMessage
    };
  } catch (error) {
    console.error("Erro ao enviar transação:", error);
    throw error;
  }
}

// ========== TRANSAÇÕES DO QUIZ ==========

/**
 * Minta um Quiz Pass NFT
 */
export async function mintQuizPass() {
  const cadence = `
    import QuizPassNFT from ${CONTRACT_ADDRESSES.QuizPassNFT}

    transaction {
      prepare(signer: AuthAccount) {
        // Mint NFT para o signer
        QuizPassNFT.mintPass(recipient: signer.address)
      }
    }
  `;

  return await sendTransaction(cadence);
}

/**
 * Participa do quiz
 */
export async function submitQuizAnswers(answers) {
  const cadence = `
    import QuizRace from ${CONTRACT_ADDRESSES.QuizRace}

    transaction(answers: [String]) {
      prepare(signer: AuthAccount) {
        // Submete respostas
        QuizRace.submitAnswers(
          user: signer,
          answers: answers
        )
      }
    }
  `;

  return await sendTransaction(cadence, [answers]);
}

/**
 * Verifica se tem Quiz Pass NFT
 */
export async function hasQuizPass(address) {
  const cadence = `
    import QuizPassNFT from ${CONTRACT_ADDRESSES.QuizPassNFT}

    pub fun main(address: Address): Bool {
      return QuizPassNFT.hasValidPass(address: address)
    }
  `;

  return await executeScript(cadence, [
    fcl.arg(address, fcl.t.Address)
  ]);
}

// ========== FLOW ACTIONS ==========

/**
 * Executa swap usando Flow Actions
 */
export async function executeSwap(fromToken, toToken, amount) {
  const cadence = `
    import FlowAgentActions from ${CONTRACT_ADDRESSES.FlowAgentActions}

    transaction(fromToken: String, toToken: String, amount: UFix64) {
      execute {
        FlowAgentActions.swap(
          from: fromToken,
          to: toToken,
          amount: amount
        )
      }
    }
  `;

  return await sendTransaction(cadence, [
    fcl.arg(fromToken, fcl.t.String),
    fcl.arg(toToken, fcl.t.String),
    fcl.arg(amount.toFixed(8), fcl.t.UFix64)
  ]);
}

// ========== UTILS ==========

/**
 * Formata endereço Flow
 */
export function formatAddress(address) {
  if (!address) return "";
  // Remove 0x e pega primeiros e últimos caracteres
  const clean = address.replace("0x", "");
  if (clean.length <= 8) return address;
  return `0x${clean.slice(0, 4)}...${clean.slice(-4)}`;
}

/**
 * Formata saldo FLOW
 */
export function formatFlow(amount) {
  return `${parseFloat(amount).toFixed(2)} FLOW`;
}

export default {
  fcl,
  connectWallet,
  disconnectWallet,
  getAccount,
  getFlowBalance,
  executeScript,
  sendTransaction,
  mintQuizPass,
  submitQuizAnswers,
  hasQuizPass,
  executeSwap,
  formatAddress,
  formatFlow
};