"""
Servidor FastAPI - Proxy REST para Claude Code SDK
Baseado no projeto cc-sdk-chat funcional
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import uuid
import os
import sys
import aiohttp
from typing import Dict, Any, AsyncGenerator, Optional
from datetime import datetime

# Adicionar paths do SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sdk'))

# Importar módulo FNS
# from find import FindNameService, setup_fns_endpoints
# from find.quiz import QuizChatIntegration

# Importar handler e session manager
from core.claude_handler import ClaudeHandler, SessionConfig
from core.session_manager import ClaudeCodeSessionManager

# Inicializar FastAPI
app = FastAPI(
    title="Neo4j Agent - Hackathon Flow Blockchain Agents Proxy",
    description="Proxy REST que encapsula Claude Code SDK com SSE streaming",
    version="1.0.0"
)

# CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar handlers
claude_handler = ClaudeHandler()
session_manager = ClaudeCodeSessionManager()

# Inicializar FNS
# fns_service = FindNameService()
# quiz_integration = QuizChatIntegration()

# Models Pydantic
class ChatMessage(BaseModel):
    message: str
    session_id: str = None
    project_id: str = "neo4j-agent"

class SessionCreate(BaseModel):
    project_id: str = "neo4j-agent"
    config: Dict[str, Any] = {}

# Health check
@app.get("/api/health")
async def health_check():
    """Verificação de saúde do servidor."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Hackathon Flow Blockchain Agents Proxy",
        "sdk_available": True,
        "sessions_active": len(session_manager.get_active_sessions())
    }

# Endpoint principal de chat com SSE
@app.post("/api/chat")
async def chat_stream(chat_message: ChatMessage):
    """
    Endpoint principal para chat com Claude via SSE.
    Usa o ClaudeHandler para processar mensagens.
    """

    async def generate_sse() -> AsyncGenerator[str, None]:
        """Gera eventos SSE para streaming."""

        try:
            # Criar ou recuperar sessão
            if not chat_message.session_id:
                session_id = str(uuid.uuid4())
                # Criar nova sessão
                session_config = SessionConfig(
                    project_id=chat_message.project_id,
                    temperature=0.7,
                    model="claude-3-5-sonnet-20241022"
                )
                await claude_handler.create_session(session_id, session_config)

                # Notificar criação de sessão
                yield f"data: {json.dumps({'type': 'session_created', 'session_id': session_id})}\n\n"
            else:
                session_id = chat_message.session_id

            # Verificar se é comando FNS antes de enviar para Claude
            # fns_command = fns_service.parse_command(chat_message.message)

            # if fns_command:
            #     # Processar comando FNS
            #     fns_result = await fns_service.process_command(fns_command)
            #     formatted_response = fns_service.format_response(fns_result)

            #     # Enviar resposta FNS via SSE
            #     yield f"data: {json.dumps({'type': 'message', 'content': formatted_response})}\n\n"

            # # Verificar se é comando de quiz
            # elif chat_message.message.lower().startswith("quiz"):
            #     quiz_response = await quiz_integration.handle_quiz_command(session_id, chat_message.message)
            #     yield f"data: {json.dumps({'type': 'message', 'content': quiz_response})}\n\n"

            # else:
            # Processar mensagem normal com Claude Handler
            if True:
                async for chunk in claude_handler.send_message(session_id, chat_message.message):
                    # Enviar chunk via SSE
                    yield f"data: {json.dumps(chunk)}\n\n"

                    # Pequena pausa para streaming suave
                    await asyncio.sleep(0.01)

            # Evento final
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

        except Exception as e:
            # Enviar erro via SSE
            error_data = {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    # Retornar streaming response
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Criar nova sessão
@app.post("/api/sessions")
async def create_session(session_create: SessionCreate):
    """Cria uma nova sessão de chat."""

    session_id = str(uuid.uuid4())

    try:
        # Configurar sessão
        session_config = SessionConfig(
            project_id=session_create.project_id,
            **session_create.config
        )

        # Criar sessão no handler
        await claude_handler.create_session(session_id, session_config)

        # Registrar no session manager
        session_manager.create_session(
            session_id=session_id,
            project_id=session_create.project_id
        )

        return {
            "session_id": session_id,
            "project_id": session_create.project_id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Listar sessões ativas
@app.get("/api/sessions")
async def list_sessions():
    """Lista todas as sessões ativas."""

    active_sessions = session_manager.get_active_sessions()

    return {
        "sessions": [
            {
                "session_id": session_id,
                "project_id": session.project_id,
                "created_at": session.created_at.isoformat(),
                "messages_count": len(session.messages)
            }
            for session_id, session in active_sessions.items()
        ],
        "total": len(active_sessions)
    }

# Deletar sessão
@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Deleta uma sessão específica."""

    try:
        # Remover do handler
        if hasattr(claude_handler, 'close_session'):
            await claude_handler.close_session(session_id)

        # Remover do session manager
        session_manager.close_session(session_id)

        return {
            "session_id": session_id,
            "status": "deleted",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Status do SDK
@app.get("/api/sdk-status")
async def sdk_status():
    """Retorna status do Claude Code SDK."""

    try:
        # Verificar se SDK está disponível
        from sdk.claude_code_sdk import query
        sdk_available = True
        sdk_info = "Claude Code SDK disponível e funcional"
    except ImportError:
        sdk_available = False
        sdk_info = "Claude Code SDK não disponível - verificar instalação"

    return {
        "sdk_available": sdk_available,
        "info": sdk_info,
        "handler_status": "active" if claude_handler else "inactive",
        "sessions_active": len(session_manager.get_active_sessions()),
        "timestamp": datetime.now().isoformat()
    }

# Endpoint para buscar saldo Flow
@app.get("/api/flow/balance/{address}")
async def get_flow_balance(address: str):
    """
    Busca o saldo de uma conta Flow na testnet.
    """
    # Remove 0x prefix se presente
    if address.startswith('0x'):
        address = address[2:]

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://rest-testnet.onflow.org/v1/accounts/{address}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    balance = int(data.get('balance', 0))
                    flow_balance = balance / 100_000_000

                    # Formatar para mostrar 101,000 sem decimais desnecessários
                    if flow_balance >= 1000:
                        balance_formatted = f"{flow_balance:,.0f}"
                    else:
                        balance_formatted = f"{flow_balance:.4f} FLOW"

                    return {
                        "address": f"0x{address}",
                        "balance": flow_balance,
                        "balance_formatted": balance_formatted,
                        "network": "testnet",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Account not found on testnet: {address}"
                    )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Flow testnet: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching balance: {str(e)}"
        )

# Endpoint simplificado para o saldo padrão
@app.get("/api/flow/balance")
async def get_default_flow_balance():
    """
    Busca o saldo da conta padrão do projeto na testnet.
    """
    # Conta com 101,000 FLOW
    default_address = "0x36395f9dde50ea27"
    return await get_flow_balance(default_address)

# ========== ENDPOINTS FNS COM NEO4J ==========

# @app.get("/api/fns/participant/{address}/names")
# async def get_participant_names(address: str):
#     """Retorna todos os nomes que um participante possui"""
#     try:
#         from find.neo4j_integration import FNSNeo4jIntegration
#         neo4j = FNSNeo4jIntegration()
#         names = neo4j.get_participant_names(address)
#         neo4j.close()
#         return {"address": address, "names": names, "total": len(names)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/fns/participant/{address}/badges")
# async def get_participant_badges(address: str):
#     """Retorna badges conquistados por um participante"""
#     try:
#         from find.neo4j_integration import FNSNeo4jIntegration
#         neo4j = FNSNeo4jIntegration()
#         badges = neo4j.get_participant_badges(address)
#         neo4j.close()
#         return {"address": address, "badges": badges}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/fns/statistics")
# async def get_fns_statistics():
#     """Retorna estatísticas gerais do bootcamp"""
#     try:
#         from find.neo4j_integration import FNSNeo4jIntegration
#         neo4j = FNSNeo4jIntegration()
#         stats = neo4j.get_event_statistics()
#         neo4j.close()
#         return stats
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/fns/leaderboard")
# async def get_quiz_leaderboard(limit: int = 10):
#     """Retorna leaderboard do quiz"""
#     try:
#         from find.neo4j_integration import FNSNeo4jIntegration
#         neo4j = FNSNeo4jIntegration()
#         leaderboard = neo4j.get_leaderboard(limit)
#         neo4j.close()
#         return {"leaderboard": leaderboard, "limit": limit}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/fns/search/{pattern}")
# async def search_names(pattern: str):
#     """Busca nomes por padrão"""
#     try:
#         from find.neo4j_integration import FNSNeo4jIntegration
#         neo4j = FNSNeo4jIntegration()
#         names = neo4j.search_names_by_pattern(pattern)
#         neo4j.close()
#         return {"pattern": pattern, "results": names, "total": len(names)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Inicialização
@app.on_event("startup")
async def startup_event():
    """Inicialização do servidor."""
    print("=" * 60)
    print("🚀 PROXY REST - Claude Code SDK")
    print("=" * 60)
    print("📡 Servidor iniciado na porta 8991")
    print("🔌 Endpoint principal: POST /api/chat")
    print("📊 Health check: GET /api/health")
    print("🔍 SDK status: GET /api/sdk-status")
    # print("🔍 FNS integrado: resolve, check, register, quiz")
    print("=" * 60)

    # Configurar endpoints FNS
    # await setup_fns_endpoints(app)

@app.on_event("shutdown")
async def shutdown_event():
    """Desligamento do servidor."""
    # Fechar todas as sessões
    for session_id in list(session_manager.get_active_sessions().keys()):
        try:
            await claude_handler.close_session(session_id)
        except:
            pass
    print("🔴 Servidor desligado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8991,
        reload=True,
        log_level="info"
    )