"""
⚡ Sistema de Energia do Submarino - Gasto Real de Flow
O participante precisa gastar Flow de verdade na testnet para energizar o submarino
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

class SubmarineEnergySystem:
    """
    Sistema onde gastar Flow na testnet = energia para o submarino subir
    Cada Flow gasto = energia para escapar das profundezas
    """

    def __init__(self):
        self.testnet_api = "https://rest-testnet.onflow.org"
        self.submarine_wallet = "0x25f823e2a115b2dc"  # Carteira do submarino

        # Tabela de conversão Flow -> Energia
        self.energy_conversion = {
            "register_name": {
                "flow_cost": 5.0,  # Custo em Flow (standard)
                "energy_gained": 50,  # Energia ganha
                "depth_reduction": 25  # Metros subidos
            },
            "premium_name": {
                "flow_cost": 15.0,  # Nome premium
                "energy_gained": 100,
                "depth_reduction": 50
            },
            "exclusive_name": {
                "flow_cost": 50.0,  # Nome exclusivo
                "energy_gained": 250,
                "depth_reduction": 100
            },
            "energy_boost_small": {
                "flow_cost": 1.0,
                "energy_gained": 10,
                "depth_reduction": 5
            },
            "energy_boost_medium": {
                "flow_cost": 3.0,
                "energy_gained": 35,
                "depth_reduction": 15
            },
            "energy_boost_large": {
                "flow_cost": 10.0,
                "energy_gained": 120,
                "depth_reduction": 50
            },
            "quiz_entry": {
                "flow_cost": 0.5,  # Taxa para entrar no quiz
                "energy_gained": 5,
                "depth_reduction": 2
            },
            "help_friend": {
                "flow_cost": 2.0,  # Ajudar outro participante
                "energy_gained": 30,
                "depth_reduction": 12
            },
            "unlock_compartment": {
                "flow_cost": 0.1,  # Desbloquear novo compartimento
                "energy_gained": 2,
                "depth_reduction": 1
            }
        }

        # Registro de transações
        self.energy_transactions = []

        # Cache de saldos
        self.balance_cache = {}

    async def check_participant_balance(self, address: str) -> float:
        """
        Verifica saldo real do participante na testnet
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.testnet_api}/v1/accounts/{address.replace('0x', '')}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        balance = int(data.get('balance', 0)) / 100_000_000
                        self.balance_cache[address] = balance
                        return balance
        except Exception as e:
            print(f"Erro ao verificar saldo: {e}")
            return self.balance_cache.get(address, 0)

        return 0

    async def spend_flow_for_energy(
        self,
        participant_address: str,
        action_type: str,
        amount_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Gasta Flow real para ganhar energia no submarino

        Args:
            participant_address: Endereço do participante
            action_type: Tipo de ação (da tabela de conversão)
            amount_override: Valor customizado de Flow a gastar

        Returns:
            Resultado da transação com energia ganha
        """

        # Verificar saldo atual
        current_balance = await self.check_participant_balance(participant_address)

        # Determinar custo e recompensas
        if action_type in self.energy_conversion:
            config = self.energy_conversion[action_type]
            flow_cost = amount_override or config["flow_cost"]

            # Calcular energia proporcional se valor customizado
            if amount_override:
                ratio = amount_override / config["flow_cost"]
                energy_gained = int(config["energy_gained"] * ratio)
                depth_reduction = int(config["depth_reduction"] * ratio)
            else:
                energy_gained = config["energy_gained"]
                depth_reduction = config["depth_reduction"]
        else:
            # Ação customizada - calcular dinamicamente
            flow_cost = amount_override or 1.0
            energy_gained = int(flow_cost * 10)  # 10 energia por Flow
            depth_reduction = int(flow_cost * 5)  # 5 metros por Flow

        # Verificar se tem saldo suficiente
        if current_balance < flow_cost:
            return {
                "success": False,
                "error": "Saldo insuficiente",
                "current_balance": current_balance,
                "required": flow_cost,
                "message": f"""
⚠️ **ENERGIA INSUFICIENTE!**

O submarino precisa de {flow_cost} FLOW para realizar esta ação!
Seu saldo atual: {current_balance:.2f} FLOW

💡 Dica: Complete desafios menores para ganhar Flow ou peça ajuda a outros surfistas!
                """
            }

        # Simular transação (em produção seria uma transação real Cadence)
        transaction = {
            "from": participant_address,
            "to": self.submarine_wallet,
            "amount": flow_cost,
            "purpose": action_type,
            "timestamp": datetime.now().isoformat(),
            "energy_gained": energy_gained,
            "depth_reduction": depth_reduction
        }

        # Registrar transação
        self.energy_transactions.append(transaction)

        # Atualizar cache de saldo
        self.balance_cache[participant_address] = current_balance - flow_cost

        return {
            "success": True,
            "transaction": transaction,
            "energy_gained": energy_gained,
            "depth_reduction": depth_reduction,
            "new_balance": current_balance - flow_cost,
            "message": f"""
⚡ **ENERGIA TRANSFERIDA COM SUCESSO!**

💰 Flow gasto: {flow_cost} FLOW
⚡ Energia ganha: +{energy_gained} pontos
🆙 Submarino subiu: {depth_reduction} metros!
💎 Novo saldo: {current_balance - flow_cost:.2f} FLOW

O submarino agradece sua contribuição! Cada Flow gasto nos aproxima da superfície!
            """
        }

    async def get_energy_shop(self) -> Dict[str, Any]:
        """
        Retorna a "loja" de energia - opções de gasto de Flow
        """
        return {
            "title": "🏪 LOJA DE ENERGIA DO SUBMARINO",
            "description": "Gaste Flow para energizar o submarino e subir!",
            "options": [
                {
                    "id": "energy_boost_small",
                    "name": "⚡ Boost Pequeno",
                    "cost": self.energy_conversion["energy_boost_small"]["flow_cost"],
                    "energy": self.energy_conversion["energy_boost_small"]["energy_gained"],
                    "depth": self.energy_conversion["energy_boost_small"]["depth_reduction"],
                    "description": "Um pequeno impulso para continuar"
                },
                {
                    "id": "energy_boost_medium",
                    "name": "⚡⚡ Boost Médio",
                    "cost": self.energy_conversion["energy_boost_medium"]["flow_cost"],
                    "energy": self.energy_conversion["energy_boost_medium"]["energy_gained"],
                    "depth": self.energy_conversion["energy_boost_medium"]["depth_reduction"],
                    "description": "Boa quantidade de energia"
                },
                {
                    "id": "energy_boost_large",
                    "name": "⚡⚡⚡ Boost Grande",
                    "cost": self.energy_conversion["energy_boost_large"]["flow_cost"],
                    "energy": self.energy_conversion["energy_boost_large"]["energy_gained"],
                    "depth": self.energy_conversion["energy_boost_large"]["depth_reduction"],
                    "description": "Grande impulso rumo à superfície!"
                },
                {
                    "id": "register_name",
                    "name": "🏷️ Registrar Nome .find",
                    "cost": self.energy_conversion["register_name"]["flow_cost"],
                    "energy": self.energy_conversion["register_name"]["energy_gained"],
                    "depth": self.energy_conversion["register_name"]["depth_reduction"],
                    "description": "Grave seu nome na blockchain e ganhe muita energia!"
                },
                {
                    "id": "help_friend",
                    "name": "🤝 Ajudar Outro Surfista",
                    "cost": self.energy_conversion["help_friend"]["flow_cost"],
                    "energy": self.energy_conversion["help_friend"]["energy_gained"],
                    "depth": self.energy_conversion["help_friend"]["depth_reduction"],
                    "description": "Ajude outro participante e ganhe karma!"
                }
            ],
            "tip": "💡 Quanto mais Flow você investe, mais rápido chegamos à superfície!"
        }

    def calculate_energy_needed(self, current_depth: int) -> Dict[str, Any]:
        """
        Calcula quanta energia (Flow) é necessária para chegar à superfície
        """
        # Cada metro precisa de 0.2 Flow para subir
        flow_needed = current_depth * 0.2

        # Sugerir melhor estratégia
        suggestions = []

        if flow_needed <= 1:
            suggestions.append("Um boost pequeno é suficiente!")
        elif flow_needed <= 5:
            suggestions.append("Um ou dois boosts médios devem resolver")
        elif flow_needed <= 20:
            suggestions.append("Registrar um nome .find seria muito eficiente!")
        else:
            suggestions.append("Combine várias ações para subir mais rápido")

        return {
            "current_depth": current_depth,
            "flow_needed": round(flow_needed, 2),
            "energy_needed": current_depth * 2,
            "suggestions": suggestions,
            "message": f"""
📊 **CÁLCULO DE ENERGIA**

Profundidade atual: {current_depth}m
Flow necessário: ~{flow_needed:.2f} FLOW
Energia necessária: {current_depth * 2} pontos

{' | '.join(suggestions)}
            """
        }

    async def process_group_contribution(
        self,
        contributors: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Processa contribuição em grupo - vários surfistas ajudam com Flow

        Args:
            contributors: Lista de {"address": "0x...", "amount": 1.0}
        """
        total_flow = sum(c["amount"] for c in contributors)
        total_energy = int(total_flow * 15)  # Bonus por cooperação
        total_depth = int(total_flow * 8)

        results = []
        for contributor in contributors:
            # Verificar saldo de cada um
            balance = await self.check_participant_balance(contributor["address"])
            if balance >= contributor["amount"]:
                results.append({
                    "address": contributor["address"],
                    "contributed": contributor["amount"],
                    "success": True
                })
            else:
                results.append({
                    "address": contributor["address"],
                    "requested": contributor["amount"],
                    "available": balance,
                    "success": False
                })

        successful = [r for r in results if r["success"]]

        if successful:
            actual_total = sum(r["contributed"] for r in successful)
            actual_energy = int(actual_total * 15)
            actual_depth = int(actual_total * 8)

            return {
                "success": True,
                "contributors": len(successful),
                "total_flow": actual_total,
                "total_energy": actual_energy,
                "depth_reduction": actual_depth,
                "message": f"""
🤝 **CONTRIBUIÇÃO EM GRUPO BEM SUCEDIDA!**

{len(successful)} surfistas contribuíram com {actual_total:.2f} FLOW!
⚡ Energia total: +{actual_energy} pontos
🆙 Subimos: {actual_depth} metros!

A união faz a força! Juntos somos mais fortes! 🌊
                """
            }

        return {
            "success": False,
            "error": "Nenhum participante conseguiu contribuir",
            "details": results
        }

    def get_transaction_history(self, participant_address: Optional[str] = None) -> List[Dict]:
        """
        Retorna histórico de transações de energia
        """
        if participant_address:
            return [t for t in self.energy_transactions if t["from"] == participant_address]
        return self.energy_transactions

    def calculate_roi(self, participant_address: str) -> Dict[str, Any]:
        """
        Calcula o retorno sobre investimento em Flow
        """
        transactions = self.get_transaction_history(participant_address)

        if not transactions:
            return {
                "total_spent": 0,
                "total_energy": 0,
                "total_depth_reduced": 0,
                "efficiency": 0,
                "message": "Você ainda não investiu Flow no submarino"
            }

        total_spent = sum(t["amount"] for t in transactions)
        total_energy = sum(t["energy_gained"] for t in transactions)
        total_depth = sum(t["depth_reduction"] for t in transactions)
        efficiency = total_energy / total_spent if total_spent > 0 else 0

        return {
            "total_spent": total_spent,
            "total_energy": total_energy,
            "total_depth_reduced": total_depth,
            "efficiency": round(efficiency, 2),
            "average_cost_per_meter": round(total_spent / total_depth, 4) if total_depth > 0 else 0,
            "message": f"""
📊 **SEU INVESTIMENTO NO RESGATE**

💰 Total investido: {total_spent:.2f} FLOW
⚡ Energia total gerada: {total_energy} pontos
🆙 Metros totais subidos: {total_depth}m
📈 Eficiência: {efficiency:.2f} energia/FLOW

Cada Flow investido nos aproximou {total_depth/total_spent:.1f}m da superfície!
            """
        }


# ========== INTEGRAÇÃO COM O CHAT ==========

class EnergySystemChat:
    """Integração do sistema de energia com o chat"""

    def __init__(self):
        self.energy_system = SubmarineEnergySystem()

    async def process_energy_command(self, participant: str, message: str) -> str:
        """
        Processa comandos relacionados a energia
        """
        message_lower = message.lower()

        # Verificar saldo
        if "saldo" in message_lower or "balance" in message_lower:
            balance = await self.energy_system.check_participant_balance(participant)
            return f"""
💰 **SEU SALDO NA TESTNET**

Você possui: {balance:.4f} FLOW
Equivale a: {int(balance * 10)} pontos de energia potencial

Use seus Flow para energizar o submarino e subir!
Digite "loja" para ver as opções de energia.
            """

        # Mostrar loja
        elif "loja" in message_lower or "shop" in message_lower:
            shop = await self.energy_system.get_energy_shop()
            items = "\n".join([
                f"{i+1}. {opt['name']} - {opt['cost']} FLOW ({opt['description']})"
                for i, opt in enumerate(shop['options'])
            ])
            return f"""
{shop['title']}
{shop['description']}

{items}

Digite o número da opção ou o nome para comprar energia!
            """

        # Comprar energia
        elif any(word in message_lower for word in ["boost", "energia", "comprar"]):
            # Detectar tipo de boost
            if "pequen" in message_lower:
                action = "energy_boost_small"
            elif "medi" in message_lower:
                action = "energy_boost_medium"
            elif "grand" in message_lower:
                action = "energy_boost_large"
            else:
                action = "energy_boost_small"

            result = await self.energy_system.spend_flow_for_energy(participant, action)
            return result["message"]

        # Calcular necessidade
        elif "calcular" in message_lower or "quanto" in message_lower:
            # Assumir profundidade atual de 75m
            calc = self.energy_system.calculate_energy_needed(75)
            return calc["message"]

        # Histórico
        elif "historico" in message_lower or "history" in message_lower:
            roi = self.energy_system.calculate_roi(participant)
            return roi["message"]

        return "Digite 'loja' para ver opções de energia ou 'saldo' para ver seu Flow!"


# ========== Exemplo de Uso ==========

if __name__ == "__main__":
    async def demo():
        print("=" * 60)
        print("⚡ SISTEMA DE ENERGIA DO SUBMARINO")
        print("=" * 60)

        system = SubmarineEnergySystem()
        chat = EnergySystemChat()

        # Simular participante
        participant = "0x123abc"

        # Verificar saldo
        balance = await system.check_participant_balance("0x25f823e2a115b2dc")
        print(f"\n💰 Saldo inicial: {balance} FLOW")

        # Mostrar loja
        shop = await system.get_energy_shop()
        print(f"\n{shop['title']}")

        # Comprar energia
        result = await system.spend_flow_for_energy(
            participant,
            "energy_boost_medium",
            3.0
        )
        print(f"\n{result['message']}")

        # Calcular necessidade
        calc = system.calculate_energy_needed(100)
        print(f"\n{calc['message']}")

    asyncio.run(demo())