"""
API Endpoints para .find Name Service
Adiciona funcionalidades de compra de nomes .find via API/Chat
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import subprocess
import json
import os
from datetime import datetime
from find_name_agent import FindNameServiceAgent

# ========================================
# MODELS PARA .FIND
# ========================================

class RegisterFindName(BaseModel):
    """Model para registrar nome .find"""
    name: str  # Nome sem .find
    buyer_address: Optional[str] = None
    payment_amount: float = 5.0  # FLOW tokens

class ResolveFindName(BaseModel):
    """Model para resolver nome"""
    name: str  # Com ou sem .find

class CheckFindAvailability(BaseModel):
    """Model para verificar disponibilidade"""
    name: str

class ListFindForSale(BaseModel):
    """Model para listar nome à venda"""
    name: str
    price: float
    seller_address: Optional[str] = None

class BuyFindName(BaseModel):
    """Model para comprar nome listado"""
    name: str
    max_price: float
    buyer_address: Optional[str] = None

# ========================================
# ENDPOINTS .FIND PARA ADICIONAR AO FLOW-SERVER
# ========================================

def add_find_endpoints(app: FastAPI):
    """
    Adiciona endpoints .find ao servidor Flow existente
    """

    # Inicializa agente
    find_agent = FindNameServiceAgent(network=os.getenv("FLOW_NETWORK", "testnet"))

    # ===================================
    # COMPRAR NOME .FIND
    # ===================================

    @app.post("/api/find/register")
    async def register_find_name(request: RegisterFindName):
        """
        Registra (compra) um novo nome .find

        Exemplo via chat:
        "Compre o nome alice.find para mim"
        """
        try:
            # Limpa o nome (remove .find se incluído)
            clean_name = request.name.replace(".find", "")

            # Verifica disponibilidade primeiro
            check_script = f'''
            import FIND from {find_agent.contracts["FIND"]}

            pub fun main(name: String): Bool {{
                return FIND.lookupAddress(name) == nil
            }}
            '''

            # Executa verificação
            cmd = [
                "flow", "scripts", "execute",
                "--code", check_script,
                "--arg", f'String:"{clean_name}"',
                "--network", os.getenv("FLOW_NETWORK", "testnet")
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if "false" in result.stdout:
                raise HTTPException(
                    status_code=400,
                    detail=f"Nome {clean_name}.find já está registrado!"
                )

            # Prepara transação de registro
            register_tx = find_agent.register_name_script(
                name=clean_name,
                amount=request.payment_amount
            )

            # Retorna transação preparada (frontend assina)
            return {
                "success": True,
                "name": f"{clean_name}.find",
                "price": request.payment_amount,
                "status": "available",
                "transaction": {
                    "cadence": register_tx,
                    "args": [
                        {"type": "String", "value": clean_name},
                        {"type": "UFix64", "value": str(request.payment_amount)}
                    ]
                },
                "message": f"Nome {clean_name}.find está disponível! Assine a transação para registrar.",
                "timestamp": datetime.now().isoformat()
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================================
    # VERIFICAR DISPONIBILIDADE
    # ===================================

    @app.post("/api/find/check")
    async def check_find_availability(request: CheckFindAvailability):
        """
        Verifica se nome .find está disponível

        Exemplo via chat:
        "O nome pedro.find está disponível?"
        """
        try:
            clean_name = request.name.replace(".find", "")

            # Script de verificação
            script = find_agent.resolve_name_script(clean_name)

            cmd = [
                "flow", "scripts", "execute",
                "--code", script,
                "--arg", f'String:"{clean_name}"',
                "--network", os.getenv("FLOW_NETWORK", "testnet")
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            is_available = "nil" in result.stdout
            current_owner = None if is_available else result.stdout.strip()

            response = {
                "name": f"{clean_name}.find",
                "available": is_available,
                "current_owner": current_owner,
                "registration_price": 5.0,  # Preço padrão
                "timestamp": datetime.now().isoformat()
            }

            if is_available:
                response["message"] = f"🎉 {clean_name}.find está disponível para registro!"
                response["action"] = "Você pode registrar este nome agora"
            else:
                response["message"] = f"❌ {clean_name}.find já está registrado"
                response["action"] = "Tente outro nome ou verifique se está à venda"

            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================================
    # RESOLVER NOME PARA ENDEREÇO
    # ===================================

    @app.post("/api/find/resolve")
    async def resolve_find_name(request: ResolveFindName):
        """
        Resolve nome .find para endereço Flow

        Exemplo via chat:
        "Qual o endereço de alice.find?"
        """
        try:
            clean_name = request.name.replace(".find", "")

            script = find_agent.resolve_name_script(clean_name)

            cmd = [
                "flow", "scripts", "execute",
                "--code", script,
                "--arg", f'String:"{clean_name}"',
                "--network", os.getenv("FLOW_NETWORK", "testnet")
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if "nil" in result.stdout:
                return {
                    "name": f"{clean_name}.find",
                    "address": None,
                    "found": False,
                    "message": f"Nome {clean_name}.find não encontrado",
                    "timestamp": datetime.now().isoformat()
                }

            address = result.stdout.strip()

            return {
                "name": f"{clean_name}.find",
                "address": address,
                "found": True,
                "message": f"✅ {clean_name}.find → {address}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================================
    # BUSCAR MEU NOME .FIND
    # ===================================

    @app.get("/api/find/my-names/{address}")
    async def get_my_find_names(address: str):
        """
        Lista todos os nomes .find de um endereço

        Exemplo via chat:
        "Quais são meus nomes .find?"
        """
        try:
            script = find_agent.get_all_names_script(address)

            cmd = [
                "flow", "scripts", "execute",
                "--code", script,
                "--arg", f'Address:{address}',
                "--network", os.getenv("FLOW_NETWORK", "testnet")
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Parse resultado
            names = []
            if result.stdout and "[]" not in result.stdout:
                # Extrair nomes do output
                names_raw = result.stdout.strip().replace("[", "").replace("]", "")
                if names_raw:
                    names = [n.strip().strip('"') for n in names_raw.split(",")]

            return {
                "address": address,
                "names": [f"{n}.find" for n in names],
                "count": len(names),
                "message": f"Você tem {len(names)} nome(s) .find",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================================
    # BUSCAR NOMES DISPONÍVEIS
    # ===================================

    @app.post("/api/find/search")
    async def search_find_names(pattern: str, limit: int = 10):
        """
        Busca nomes .find por padrão

        Exemplo via chat:
        "Mostre nomes .find com 'flow'"
        """
        try:
            # Lista de nomes comuns para sugerir
            suggestions = []
            base_names = [
                f"{pattern}",
                f"{pattern}dao",
                f"{pattern}nft",
                f"{pattern}defi",
                f"{pattern}web3",
                f"the{pattern}",
                f"{pattern}flow",
                f"{pattern}2024",
                f"super{pattern}",
                f"{pattern}coin"
            ]

            for name in base_names[:limit]:
                # Verifica cada sugestão
                check_result = await check_find_availability(
                    CheckFindAvailability(name=name)
                )

                suggestions.append({
                    "name": f"{name}.find",
                    "available": check_result["available"],
                    "price": 5.0 if check_result["available"] else None
                })

            available_count = sum(1 for s in suggestions if s["available"])

            return {
                "pattern": pattern,
                "suggestions": suggestions,
                "available_count": available_count,
                "total_checked": len(suggestions),
                "message": f"Encontrei {available_count} nomes disponíveis com '{pattern}'",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================================
    # INTEGRAÇÃO COM QUIZ
    # ===================================

    @app.post("/api/find/quiz-register")
    async def register_quiz_participant_name(participant_name: str):
        """
        Registra nome especial para participante do Quiz

        Exemplo via chat:
        "Registre meu nome para o quiz: joão"
        """
        try:
            # Cria nome especial do bootcamp
            quiz_name = f"{participant_name}-bootcamp2024"

            # Verifica disponibilidade
            check = await check_find_availability(
                CheckFindAvailability(name=quiz_name)
            )

            if not check["available"]:
                # Sugere alternativas
                alternatives = [
                    f"{participant_name}-quiz2024",
                    f"{participant_name}-flow2024",
                    f"{participant_name}-hackathon"
                ]

                return {
                    "success": False,
                    "requested_name": f"{quiz_name}.find",
                    "available": False,
                    "alternatives": [f"{a}.find" for a in alternatives],
                    "message": f"Nome {quiz_name}.find já existe. Tente uma alternativa!",
                    "timestamp": datetime.now().isoformat()
                }

            # Prepara registro com desconto especial
            register_tx = find_agent.register_quiz_name(
                participant=participant_name,
                bootcamp_id="bootcamp2024"
            )

            return {
                "success": True,
                "quiz_name": f"{quiz_name}.find",
                "participant": participant_name,
                "special_price": 1.0,  # Preço especial para quiz
                "transaction": {
                    "cadence": register_tx,
                    "args": [
                        {"type": "String", "value": participant_name},
                        {"type": "String", "value": "bootcamp2024"}
                    ]
                },
                "benefits": {
                    "quiz_access": "✅ Acesso ao Quiz Race",
                    "permanent_name": "✅ Nome .find permanente",
                    "tradeable": "✅ Pode vender depois",
                    "profile": "✅ Perfil onchain"
                },
                "message": f"🎮 Nome {quiz_name}.find pronto para o Quiz!",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================================
    # STATUS GERAL .FIND
    # ===================================

    @app.get("/api/find/stats")
    async def get_find_stats():
        """
        Estatísticas do .find name service
        """
        return {
            "network": os.getenv("FLOW_NETWORK", "testnet"),
            "contracts": find_agent.contracts,
            "features": {
                "registration": "✅ Ativo",
                "resolution": "✅ Ativo",
                "trading": "✅ Ativo",
                "quiz_integration": "✅ Ativo"
            },
            "pricing": {
                "standard": 5.0,
                "quiz_special": 1.0,
                "bootcamp_free": True
            },
            "api_endpoints": [
                "/api/find/register - Registrar novo nome",
                "/api/find/check - Verificar disponibilidade",
                "/api/find/resolve - Resolver nome para endereço",
                "/api/find/my-names - Listar meus nomes",
                "/api/find/search - Buscar nomes por padrão",
                "/api/find/quiz-register - Registro especial para quiz"
            ],
            "timestamp": datetime.now().isoformat()
        }

# ===================================
# CHAT COMMANDS PARA .FIND
# ===================================

class FindChatCommands:
    """
    Comandos de chat para interagir com .find
    """

    @staticmethod
    def parse_find_command(message: str) -> Dict[str, Any]:
        """
        Interpreta comandos de chat sobre .find
        """
        message_lower = message.lower()

        # Comprar nome
        if any(word in message_lower for word in ["compre", "comprar", "registre", "registrar"]):
            if ".find" in message_lower:
                # Extrai nome
                import re
                match = re.search(r'(\w+)\.find', message_lower)
                if match:
                    return {
                        "action": "register",
                        "name": match.group(1),
                        "endpoint": "/api/find/register"
                    }

        # Verificar disponibilidade
        if any(word in message_lower for word in ["disponível", "disponivel", "existe", "tem"]):
            if ".find" in message_lower:
                import re
                match = re.search(r'(\w+)\.find', message_lower)
                if match:
                    return {
                        "action": "check",
                        "name": match.group(1),
                        "endpoint": "/api/find/check"
                    }

        # Resolver nome
        if any(word in message_lower for word in ["endereço", "endereco", "resolve", "qual"]):
            if ".find" in message_lower:
                import re
                match = re.search(r'(\w+)\.find', message_lower)
                if match:
                    return {
                        "action": "resolve",
                        "name": match.group(1),
                        "endpoint": "/api/find/resolve"
                    }

        # Meus nomes
        if any(word in message_lower for word in ["meus nomes", "meus .find", "tenho quantos"]):
            return {
                "action": "my_names",
                "endpoint": "/api/find/my-names"
            }

        # Quiz registration
        if "quiz" in message_lower and any(word in message_lower for word in ["nome", "registre", "participar"]):
            # Extrai nome do participante
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ["nome:", "sou", "chamo"]:
                    if i + 1 < len(words):
                        return {
                            "action": "quiz_register",
                            "participant_name": words[i + 1],
                            "endpoint": "/api/find/quiz-register"
                        }

        return {
            "action": "unknown",
            "message": "Não entendi. Tente: 'compre alice.find' ou 'alice.find está disponível?'"
        }

# ===================================
# EXEMPLO DE USO NO CHAT
# ===================================

"""
EXEMPLOS DE COMANDOS NO CHAT:

User: "Compre o nome alice.find para mim"
Bot: "🎉 alice.find está disponível por 5.0 FLOW! Conecte sua wallet para confirmar."

User: "O nome flow.find está disponível?"
Bot: "❌ flow.find já está registrado. Tente: flowdao.find, flowdefi.find"

User: "Qual o endereço de bob.find?"
Bot: "✅ bob.find → 0x01cf0e2f2f715450"

User: "Quais são meus nomes .find?"
Bot: "Você tem 3 nomes: alice.find, alice-bootcamp.find, alice2024.find"

User: "Registre meu nome para o quiz: maria"
Bot: "🎮 Nome maria-bootcamp2024.find registrado! Você pode participar do Quiz Race!"

User: "Busque nomes com 'nft'"
Bot: "Encontrei 5 disponíveis: nft.find, nftflow.find, nftdao.find, mynft.find, supernft.find"
"""