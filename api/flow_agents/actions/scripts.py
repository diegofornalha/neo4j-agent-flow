"""Script executor for Flow blockchain"""

import json
import subprocess
from typing import List, Any, Optional

class ScriptExecutor:
    """Executa scripts Cadence na Flow blockchain"""

    def __init__(self, agent):
        self.agent = agent

    async def execute(self, cadence: str, args: List[Any] = None) -> Any:
        """
        Executa um script Cadence

        Args:
            cadence: Código Cadence do script
            args: Argumentos do script

        Returns:
            Resultado do script
        """
        cmd = [
            "flow", "scripts", "execute",
            "--code", cadence,
            "--network", self.agent.network
        ]

        # Adicionar argumentos se houver
        if args:
            for arg in args:
                if isinstance(arg, dict):
                    cmd.extend(["--arg", f"{arg['type']}:{arg['value']}"])
                else:
                    cmd.extend(["--arg", str(arg)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }

            # Tentar fazer parse do resultado
            output = result.stdout.strip()
            try:
                return json.loads(output)
            except:
                return output

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_balance(self, address: str) -> Optional[float]:
        """
        Obtém o saldo de FLOW de uma conta

        Args:
            address: Endereço da conta

        Returns:
            Saldo em FLOW
        """
        cadence = f"""
        import FlowToken from 0x1654653399040a61
        import FungibleToken from 0xf233dcee88fe0abe

        pub fun main(address: Address): UFix64 {{
            let account = getAccount(address)

            if let vaultRef = account
                .getCapability(/public/flowTokenBalance)
                .borrow<&FlowToken.Vault{{FungibleToken.Balance}}>() {{
                return vaultRef.balance
            }}

            return 0.0
        }}
        """

        result = await self.execute(
            cadence,
            [{"type": "Address", "value": address}]
        )

        if isinstance(result, (int, float)):
            return float(result) / 100000000  # Converter para FLOW
        return None

    async def get_nft_collection(self, address: str, collection_path: str) -> List[int]:
        """
        Obtém IDs de NFTs em uma coleção

        Args:
            address: Endereço da conta
            collection_path: Path da coleção

        Returns:
            Lista de IDs de NFTs
        """
        cadence = f"""
        pub fun main(address: Address): [UInt64] {{
            let account = getAccount(address)

            if let collection = account
                .getCapability({collection_path})
                .borrow<&{{NonFungibleToken.CollectionPublic}}>() {{
                return collection.getIDs()
            }}

            return []
        }}
        """

        result = await self.execute(
            cadence,
            [{"type": "Address", "value": address}]
        )

        if isinstance(result, list):
            return result
        return []

    async def query_contract(self, address: str, contract_name: str, function_name: str, args: List[Any] = None) -> Any:
        """
        Consulta uma função de contrato

        Args:
            address: Endereço do contrato
            contract_name: Nome do contrato
            function_name: Nome da função
            args: Argumentos da função

        Returns:
            Resultado da consulta
        """
        cadence = f"""
        import {contract_name} from {address}

        pub fun main({self._format_args(args)}): Any {{
            return {contract_name}.{function_name}({self._format_call_args(args)})
        }}
        """

        return await self.execute(cadence, args)

    def _format_args(self, args: List[Any]) -> str:
        """Formata argumentos para assinatura da função"""
        if not args:
            return ""

        formatted = []
        for i, arg in enumerate(args):
            if isinstance(arg, dict):
                formatted.append(f"arg{i}: {arg['type']}")
            else:
                formatted.append(f"arg{i}: Any")

        return ", ".join(formatted)

    def _format_call_args(self, args: List[Any]) -> str:
        """Formata argumentos para chamada da função"""
        if not args:
            return ""

        return ", ".join([f"arg{i}" for i in range(len(args))])