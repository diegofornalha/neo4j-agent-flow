"""
Flow FCL Integration - Bridge entre Frontend FCL e Backend API
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os

class FCLAuthRequest(BaseModel):
    """Request de autenticação FCL"""
    address: str
    nonce: str
    signatures: List[Dict[str, Any]]

class FCLTransactionRequest(BaseModel):
    """Transaction vinda do FCL"""
    cadence: str
    args: List[Any]
    authorizer: str
    proposer: str
    payer: str

class FCLBridge:
    """Bridge entre FCL (frontend) e Flow CLI (backend)"""

    def __init__(self):
        self.authenticated_users = {}

    async def prepare_transaction_for_fcl(self, cadence: str, args: List[Any]) -> Dict:
        """
        Prepara transação para ser assinada via FCL no frontend
        """
        return {
            "cadence": cadence,
            "args": self._format_args_for_fcl(args),
            "proposer": "fcl.currentUser",
            "payer": "fcl.currentUser",
            "authorizations": ["fcl.currentUser"],
            "limit": 999
        }

    def _format_args_for_fcl(self, args: List[Any]) -> List[Dict]:
        """Formata argumentos para FCL"""
        fcl_args = []
        for arg in args:
            if isinstance(arg, str) and arg.startswith("0x"):
                fcl_args.append({"type": "Address", "value": arg})
            elif isinstance(arg, (int, float)):
                fcl_args.append({"type": "UFix64", "value": str(arg)})
            elif isinstance(arg, bool):
                fcl_args.append({"type": "Bool", "value": arg})
            else:
                fcl_args.append({"type": "String", "value": str(arg)})
        return fcl_args

    async def validate_fcl_signature(self, auth: FCLAuthRequest) -> bool:
        """
        Valida assinatura FCL para autenticação
        """
        # Aqui você validaria a assinatura onchain
        # Por enquanto, retorna True para desenvolvimento
        return True

    async def build_quiz_transaction(self, user_address: str, answers: List[str]) -> Dict:
        """
        Constrói transação de quiz para FCL
        """
        cadence = '''
        import QuizRace from 0x01cf0e2f2f715450
        import QuizPassNFT from 0x01cf0e2f2f715450

        transaction(answers: [String]) {
            prepare(signer: AuthAccount) {
                // Verifica se tem NFT
                let collection = signer.borrow<&QuizPassNFT.Collection>(from: /storage/QuizPassNFT)
                    ?? panic("Você precisa do Quiz Pass NFT!")

                // Submete respostas
                QuizRace.submitAnswers(signer: signer, answers: answers)
            }
        }
        '''

        return await self.prepare_transaction_for_fcl(
            cadence=cadence,
            args=[answers]
        )

    async def build_mint_nft_transaction(self, user_address: str) -> Dict:
        """
        Constrói transação para mintar NFT via FCL
        """
        cadence = '''
        import QuizPassNFT from 0x01cf0e2f2f715450
        import NonFungibleToken from 0x631e88ae7f1d7c20

        transaction {
            prepare(signer: AuthAccount) {
                // Setup collection if needed
                if signer.borrow<&QuizPassNFT.Collection>(from: /storage/QuizPassNFT) == nil {
                    let collection <- QuizPassNFT.createEmptyCollection()
                    signer.save(<-collection, to: /storage/QuizPassNFT)
                    signer.link<&{NonFungibleToken.CollectionPublic}>(
                        /public/QuizPassNFT,
                        target: /storage/QuizPassNFT
                    )
                }

                // Mint NFT (em produção, só admin poderia)
                let nft <- QuizPassNFT.mintNFT(
                    recipient: signer.getAddress(),
                    eventName: "Flow Bootcamp 2024",
                    participantNumber: UInt64(1)
                )
            }
        }
        '''

        return await self.prepare_transaction_for_fcl(cadence=cadence, args=[])

# ========================================
# ENDPOINTS FCL para adicionar ao flow-server.py
# ========================================

fcl_bridge = FCLBridge()

async def add_fcl_endpoints(app: FastAPI):
    """Adiciona endpoints FCL ao servidor existente"""

    @app.post("/api/fcl/auth")
    async def fcl_authenticate(auth: FCLAuthRequest):
        """Autentica usuário via FCL"""
        if await fcl_bridge.validate_fcl_signature(auth):
            fcl_bridge.authenticated_users[auth.address] = {
                "address": auth.address,
                "nonce": auth.nonce,
                "authenticated_at": datetime.now().isoformat()
            }
            return {"success": True, "address": auth.address}
        raise HTTPException(status_code=401, detail="Invalid signature")

    @app.get("/api/fcl/transaction/mint-nft/{address}")
    async def get_mint_nft_transaction(address: str):
        """Retorna transação de mint NFT para FCL assinar"""
        return await fcl_bridge.build_mint_nft_transaction(address)

    @app.post("/api/fcl/transaction/quiz")
    async def get_quiz_transaction(user_address: str, answers: List[str]):
        """Retorna transação de quiz para FCL assinar"""
        return await fcl_bridge.build_quiz_transaction(user_address, answers)

    @app.get("/api/fcl/config")
    async def get_fcl_config():
        """Retorna configuração FCL para o frontend"""
        return {
            "accessNode": os.getenv("FLOW_ACCESS_NODE", "https://rest-testnet.onflow.org"),
            "discovery": "https://fcl-discovery.onflow.org/testnet/authn",
            "network": "testnet",
            "contracts": {
                "QuizRace": "0x01cf0e2f2f715450",
                "QuizPassNFT": "0x01cf0e2f2f715450",
                "FlowToken": "0x7e60df042a9c0868",
                "FungibleToken": "0x9a0766d93b6608b7",
                "NonFungibleToken": "0x631e88ae7f1d7c20"
            },
            "appDetails": {
                "title": "Quiz Race Flow Bootcamp",
                "icon": "🎮",
                "description": "Compete por 1000 FLOW!"
            }
        }

    @app.post("/api/fcl/execute")
    async def execute_fcl_transaction(tx: FCLTransactionRequest):
        """
        Recebe transação assinada do FCL e executa via Flow CLI
        """
        # Aqui você converteria a transação FCL para Flow CLI
        # e executaria usando o flow-server existente
        pass