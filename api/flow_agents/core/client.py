"""Flow blockchain client for low-level operations"""

import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

class FlowClient:
    """Cliente para interações diretas com Flow blockchain"""

    def __init__(self, network: str = "testnet"):
        """
        Inicializa o cliente Flow

        Args:
            network: Rede Flow (mainnet, testnet, emulator)
        """
        self.network = network
        self.endpoints = {
            "mainnet": "https://rest-mainnet.onflow.org",
            "testnet": "https://rest-testnet.onflow.org",
            "emulator": "http://localhost:8888"
        }
        self.endpoint = self.endpoints.get(network, self.endpoints["testnet"])

    async def get_latest_block(self) -> Dict[str, Any]:
        """
        Obtém o último bloco da blockchain

        Returns:
            Informações do bloco
        """
        try:
            cmd = [
                "flow", "blocks", "get", "latest",
                "--network", self.network,
                "--output", "json"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}

        except Exception as e:
            return {"error": str(e)}

    async def get_transaction_status(self, tx_id: str) -> Dict[str, Any]:
        """
        Obtém status de uma transação

        Args:
            tx_id: ID da transação

        Returns:
            Status da transação
        """
        try:
            cmd = [
                "flow", "transactions", "status", tx_id,
                "--network", self.network,
                "--output", "json"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "id": tx_id,
                    "status": data.get("status", "Unknown"),
                    "error": data.get("error", None),
                    "events": data.get("events", [])
                }
            else:
                return {"error": result.stderr}

        except Exception as e:
            return {"error": str(e)}

    async def get_events(self, event_type: str, start_height: int = None, end_height: int = None) -> List[Dict[str, Any]]:
        """
        Busca eventos na blockchain

        Args:
            event_type: Tipo de evento (ex: A.0x1.FlowToken.TokensDeposited)
            start_height: Altura inicial do bloco
            end_height: Altura final do bloco

        Returns:
            Lista de eventos
        """
        try:
            cmd = [
                "flow", "events", "get", event_type,
                "--network", self.network,
                "--output", "json"
            ]

            if start_height:
                cmd.extend(["--start", str(start_height)])
            if end_height:
                cmd.extend(["--end", str(end_height)])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data if isinstance(data, list) else []
            else:
                return []

        except Exception as e:
            print(f"Erro ao buscar eventos: {e}")
            return []

    async def deploy_contract(self, name: str, code: str, account_address: str) -> Dict[str, Any]:
        """
        Deploy de contrato na blockchain

        Args:
            name: Nome do contrato
            code: Código Cadence do contrato
            account_address: Endereço da conta

        Returns:
            Resultado do deploy
        """
        try:
            # Salvar contrato temporariamente
            contract_file = f"/tmp/{name}.cdc"
            with open(contract_file, "w") as f:
                f.write(code)

            cmd = [
                "flow", "accounts", "add-contract",
                name, contract_file,
                "--signer", account_address,
                "--network", self.network
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "contract": name,
                    "address": account_address,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_account_keys(self, address: str) -> List[Dict[str, Any]]:
        """
        Obtém chaves de uma conta

        Args:
            address: Endereço da conta

        Returns:
            Lista de chaves
        """
        try:
            cmd = [
                "flow", "keys", "get",
                "--address", address,
                "--network", self.network,
                "--output", "json"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("keys", [])
            else:
                return []

        except Exception as e:
            print(f"Erro ao buscar chaves: {e}")
            return []

    async def generate_key(self, sig_algo: str = "ECDSA_P256") -> Dict[str, Any]:
        """
        Gera novo par de chaves

        Args:
            sig_algo: Algoritmo de assinatura

        Returns:
            Par de chaves gerado
        """
        try:
            cmd = [
                "flow", "keys", "generate",
                "--sig-algo", sig_algo,
                "--output", "json"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}

        except Exception as e:
            return {"error": str(e)}

    async def create_account(self, public_key: str, signer_address: str) -> Dict[str, Any]:
        """
        Cria nova conta na blockchain

        Args:
            public_key: Chave pública da nova conta
            signer_address: Endereço do pagador

        Returns:
            Informações da conta criada
        """
        try:
            cmd = [
                "flow", "accounts", "create",
                "--key", public_key,
                "--signer", signer_address,
                "--network", self.network
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Extrair endereço da saída
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Address' in line:
                        address = line.split(':')[-1].strip()
                        return {
                            "success": True,
                            "address": address,
                            "public_key": public_key
                        }
                return {
                    "success": True,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_collection(self, address: str, path: str) -> Any:
        """
        Obtém coleção de uma conta

        Args:
            address: Endereço da conta
            path: Path da coleção

        Returns:
            Dados da coleção
        """
        script = f"""
        pub fun main(address: Address): [UInt64] {{
            let account = getAccount(address)
            let collection = account.getCapability({path})
                .borrow<&{{NonFungibleToken.CollectionPublic}}>()

            if let col = collection {{
                return col.getIDs()
            }}

            return []
        }}
        """

        cmd = [
            "flow", "scripts", "execute",
            "--code", script,
            "--arg", f"Address:{address}",
            "--network", self.network
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except:
            return []

    def get_network_info(self) -> Dict[str, str]:
        """
        Obtém informações da rede

        Returns:
            Informações de configuração da rede
        """
        return {
            "network": self.network,
            "endpoint": self.endpoint,
            "status": "connected" if self.network else "disconnected"
        }