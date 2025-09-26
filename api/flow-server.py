"""
Flow Native API - Servidor REST para Agentes Flow Blockchain
100% Flow Native - Sem frameworks externos
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Importações removidas - módulo find descontinuado

# Inicializar FastAPI
app = FastAPI(
    title="Flow Native Agent API",
    description="API REST para agentes autônomos na Flow Blockchain",
    version="2.0.0"
)

# CORS configuração
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# MODELS
# ========================================

class FlowTransaction(BaseModel):
    """Modelo para transações Flow"""
    cadence: str
    args: List[Any] = []
    proposer: Optional[str] = None
    payer: Optional[str] = None
    authorizations: List[str] = []
    limit: int = 999

class FlowScript(BaseModel):
    """Modelo para scripts Flow"""
    cadence: str
    args: List[Any] = []

class FlowAccount(BaseModel):
    """Modelo para conta Flow"""
    address: str

class DeployContract(BaseModel):
    """Modelo para deploy de contrato"""
    name: str
    code: str
    account: str

class TransferFlow(BaseModel):
    """Modelo para transferência de FLOW"""
    to: str
    amount: float
    from_account: Optional[str] = None

# ========================================
# ESTADO DA APLICAÇÃO
# ========================================

class FlowAgentState:
    """Estado global do agente Flow"""
    def __init__(self):
        self.active_agents = {}
        self.transaction_history = []
        self.event_subscriptions = {}
        self.monitored_addresses = set()
        self.stats = {
            "total_transactions": 0,
            "total_scripts": 0,
            "total_events": 0,
            "start_time": datetime.now()
        }

# Inicializar estado
state = FlowAgentState()

# ========================================
# ENDPOINTS - INFORMAÇÕES
# ========================================

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "name": "Flow Native Agent API",
        "version": "2.0.0",
        "blockchain": "Flow",
        "network": os.getenv("FLOW_NETWORK", "testnet"),
        "capabilities": [
            "transactions",
            "scripts",
            "account_management",
            "contract_deployment",
            "event_monitoring",
            "flow_transfers"
        ],
        "stats": state.stats,
        "uptime": str(datetime.now() - state.stats["start_time"])
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde do servidor"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "flow_network": os.getenv("FLOW_NETWORK", "testnet"),
        "access_node": os.getenv("FLOW_ACCESS_NODE", "https://rest-testnet.onflow.org"),
        "active_agents": len(state.active_agents),
        "total_transactions": state.stats["total_transactions"]
    }

# ========================================
# ENDPOINTS - TRANSAÇÕES
# ========================================

@app.post("/api/transaction")
async def execute_transaction(tx: FlowTransaction):
    """Executar transação Cadence"""
    try:
        # Construir comando Flow CLI
        cmd = [
            "flow", "transactions", "send",
            "--code", tx.cadence,
            "--network", os.getenv("FLOW_NETWORK", "testnet")
        ]

        # Adicionar argumentos
        for arg in tx.args:
            cmd.extend(["--arg", json.dumps(arg)])

        # Executar comando
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)

        # Incrementar estatísticas
        state.stats["total_transactions"] += 1

        # Adicionar ao histórico
        tx_record = {
            "id": state.stats["total_transactions"],
            "timestamp": datetime.now().isoformat(),
            "cadence": tx.cadence[:100] + "...",
            "status": "success"
        }
        state.transaction_history.append(tx_record)

        return {
            "success": True,
            "transaction_id": tx_record["id"],
            "output": result.stdout,
            "timestamp": tx_record["timestamp"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/script")
async def execute_script(script: FlowScript):
    """Executar script Cadence"""
    try:
        # Construir comando Flow CLI
        cmd = [
            "flow", "scripts", "execute",
            "--code", script.cadence,
            "--network", os.getenv("FLOW_NETWORK", "testnet")
        ]

        # Adicionar argumentos
        for arg in script.args:
            cmd.extend(["--arg", json.dumps(arg)])

        # Executar comando
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)

        # Incrementar estatísticas
        state.stats["total_scripts"] += 1

        return {
            "success": True,
            "result": result.stdout,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ENDPOINTS - CONTAS
# ========================================

@app.get("/api/account/{address}")
async def get_account(address: str):
    """Obter informações de conta Flow"""
    try:
        cmd = [
            "flow", "accounts", "get", address,
            "--network", os.getenv("FLOW_NETWORK", "testnet"),
            "--output", "json"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)

        account_data = json.loads(result.stdout)

        return {
            "address": address,
            "balance": float(account_data.get("balance", 0)) / 100000000,
            "keys": account_data.get("keys", []),
            "contracts": list(account_data.get("contracts", {}).keys()),
            "timestamp": datetime.now().isoformat()
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse account data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/account/create")
async def create_account():
    """Criar nova conta Flow"""
    try:
        cmd = [
            "flow", "accounts", "create",
            "--network", os.getenv("FLOW_NETWORK", "testnet")
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)

        # Extrair endereço da saída
        lines = result.stdout.split('\n')
        address = None
        for line in lines:
            if "Address" in line:
                address = line.split()[-1]
                break

        return {
            "success": True,
            "address": address,
            "output": result.stdout,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ENDPOINTS - TRANSFERS
# ========================================

@app.post("/api/transfer")
async def transfer_flow(transfer: TransferFlow):
    """Transferir FLOW tokens"""
    try:
        cadence = '''
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
        '''

        tx = FlowTransaction(
            cadence=cadence,
            args=[
                {"type": "UFix64", "value": str(transfer.amount)},
                {"type": "Address", "value": transfer.to}
            ]
        )

        return await execute_transaction(tx)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ENDPOINTS - CONTRATOS
# ========================================

@app.post("/api/contract/deploy")
async def deploy_contract(contract: DeployContract):
    """Deploy de contrato Cadence"""
    try:
        cmd = [
            "flow", "accounts", "add-contract",
            contract.name, contract.code,
            "--signer", contract.account,
            "--network", os.getenv("FLOW_NETWORK", "testnet")
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)

        return {
            "success": True,
            "contract": contract.name,
            "account": contract.account,
            "output": result.stdout,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ENDPOINTS - HISTÓRICO
# ========================================

@app.get("/api/history/transactions")
async def get_transaction_history(limit: int = 10):
    """Obter histórico de transações"""
    return {
        "transactions": state.transaction_history[-limit:],
        "total": len(state.transaction_history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats")
async def get_stats():
    """Obter estatísticas do sistema"""
    return {
        "stats": state.stats,
        "active_agents": len(state.active_agents),
        "monitored_addresses": list(state.monitored_addresses),
        "uptime": str(datetime.now() - state.stats["start_time"]),
        "timestamp": datetime.now().isoformat()
    }

# ========================================
# WEBSOCKET - MONITORAMENTO
# ========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para monitoramento em tempo real"""
    await websocket.accept()

    try:
        while True:
            # Enviar estatísticas a cada 5 segundos
            await asyncio.sleep(5)

            data = {
                "type": "stats_update",
                "stats": state.stats,
                "active_agents": len(state.active_agents),
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send_json(data)

    except WebSocketDisconnect:
        pass

# ========================================
# INICIALIZAÇÃO
# ========================================

@app.on_event("startup")
async def startup_event():
    """Inicialização do servidor"""
    # Endpoints find removidos - sistema descontinuado

    print("=" * 60)
    print("🌊 FLOW NATIVE AGENT API")
    print("=" * 60)
    print("📡 Servidor iniciado")
    print(f"🌐 Network: {os.getenv('FLOW_NETWORK', 'testnet')}")
    print(f"🔗 Access Node: {os.getenv('FLOW_ACCESS_NODE', 'https://rest-testnet.onflow.org')}")
    print("=" * 60)
    print("📌 Endpoints disponíveis:")
    print("   POST /api/transaction - Executar transação")
    print("   POST /api/script - Executar script")
    print("   GET  /api/account/{address} - Info de conta")
    print("   POST /api/transfer - Transferir FLOW")
    print("   POST /api/contract/deploy - Deploy contrato")
    print("   GET  /api/fcl/config - Config FCL")
    print("   POST /api/fcl/auth - Autenticar via FCL")
    print("   WS   /ws - WebSocket monitoramento")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Desligamento do servidor"""
    print("🔴 Servidor Flow Native API desligado")

# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "flow-server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )