"""Transaction builder for Flow blockchain"""

import json
import subprocess
from typing import List, Dict, Any

class TransactionBuilder:
    """Constrói e envia transações para Flow blockchain"""

    def __init__(self, agent):
        self.agent = agent

    async def send(self, cadence: str, args: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Envia uma transação para a blockchain

        Args:
            cadence: Código Cadence da transação
            args: Argumentos da transação

        Returns:
            Resultado da transação
        """
        cmd = [
            "flow", "transactions", "send",
            "--code", cadence,
            "--network", self.agent.network,
            "--signer", self.agent.account_address
        ]

        # Adicionar argumentos
        if args:
            for arg in args:
                cmd.extend(["--arg", f"{arg['type']}:{arg['value']}"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }

            return {
                "success": True,
                "output": result.stdout,
                "transaction_id": self._extract_tx_id(result.stdout)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _extract_tx_id(self, output: str) -> str:
        """Extrai o ID da transação da saída"""
        lines = output.split('\n')
        for line in lines:
            if 'Transaction ID' in line:
                return line.split(':')[-1].strip()
        return ""