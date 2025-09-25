#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificador robusto de saldo Flow
Funciona com mainnet e testnet
"""

import json
import os
import sys
import subprocess
from typing import Optional, Dict, Any

# Configura encoding UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class FlowBalanceChecker:
    def __init__(self):
        self.api_urls = {
            'mainnet': 'https://rest-mainnet.onflow.org',
            'testnet': 'https://rest-testnet.onflow.org',
            'emulator': 'http://localhost:8888'
        }

    def normalize_address(self, address: str) -> str:
        """Normaliza o endere\u00e7o removendo 0x e espa\u00e7os"""
        if not address:
            return ""
        # Remove 0x prefix
        address = address.lower().strip()
        if address.startswith('0x'):
            address = address[2:]
        return address

    def validate_address(self, address: str) -> bool:
        """Valida formato b\u00e1sico do endere\u00e7o"""
        if not address:
            return False
        # Endere\u00e7o Flow deve ter 16 caracteres hex
        if len(address) != 16:
            return False
        try:
            int(address, 16)
            return True
        except ValueError:
            return False

    def fetch_account_info(self, address: str, network: str = 'mainnet') -> Optional[Dict[str, Any]]:
        """Busca informa\u00e7\u00f5es da conta via API Flow"""
        api_url = self.api_urls.get(network, self.api_urls['mainnet'])

        # Monta URL completa
        url = f"{api_url}/v1/accounts/{address}"

        # Executa curl
        cmd = f'curl -s "{url}" -H "Content-Type: application/json"'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)

                # Verifica se \u00e9 erro
                if 'code' in data and data['code'] >= 400:
                    return None

                return data
        except (json.JSONDecodeError, Exception) as e:
            print(f"\u274c Erro ao buscar dados: {e}")
            return None

    def display_account_info(self, address: str, network: str = 'mainnet'):
        """Exibe informa\u00e7\u00f5es formatadas da conta"""

        # Normaliza e valida endere\u00e7o
        normalized_address = self.normalize_address(address)

        print("=" * 60)
        print("💰 VERIFICADOR DE SALDO FLOW")
        print("=" * 60)

        if not self.validate_address(normalized_address):
            print(f"\u274c Endere\u00e7o inv\u00e1lido: {address}")
            print("\u2139\ufe0f  Formato esperado: 16 caracteres hexadecimais")
            print("   Exemplo: 0x1654653399040a61")
            return False

        print(f"\ud83d\udccd Endere\u00e7o: 0x{normalized_address}")
        print(f"\ud83c\udf10 Rede: {network}")
        print("-" * 60)

        # Busca dados da conta
        account_data = self.fetch_account_info(normalized_address, network)

        if not account_data:
            print(f"\u274c Conta n\u00e3o encontrada na {network}")
            print("\u2139\ufe0f  Poss\u00edveis raz\u00f5es:")
            print("   - Endere\u00e7o n\u00e3o existe nesta rede")
            print("   - Conta ainda n\u00e3o foi inicializada")
            print("   - Verifique se est\u00e1 usando a rede correta (mainnet/testnet)")

            # Sugest\u00e3o de teste com conta conhecida
            if network == 'mainnet':
                print("\n\ud83d\udd0d Teste com uma conta conhecida:")
                print("   python3 flow_balance_checker.py 0x1654653399040a61")
            return False

        # Processa e exibe dados
        balance = int(account_data.get('balance', 0))
        flow_balance = balance / 100_000_000

        print(f"\n\u2705 CONTA ENCONTRADA!")
        print(f"\ud83d\udcb0 Saldo: {flow_balance:,.8f} FLOW")

        if flow_balance >= 1:
            print(f"   \ud83d\udcb5 Equivalente a: {flow_balance:,.2f} FLOW")

        # Storage info se dispon\u00edvel
        if 'storage_capacity' in account_data:
            storage_capacity = int(account_data.get('storage_capacity', 0))
            storage_used = int(account_data.get('storage_used', 0))

            print(f"\n\ud83d\udcbe STORAGE:")
            print(f"   Capacidade: {storage_capacity:,} bytes")
            print(f"   Usado: {storage_used:,} bytes")

            if storage_capacity > 0:
                usage_percent = (storage_used / storage_capacity) * 100
                print(f"   Uso: {usage_percent:.1f}%")

        print("=" * 60)

        if flow_balance > 0:
            print("\u2705 Conta ativa com saldo!")
        else:
            print("\u26a0\ufe0f  Conta sem saldo")
            if network == 'testnet':
                print("\ud83d\udd17 Obtenha FLOW gratuito: https://testnet-faucet.onflow.org/")

        return True

def main():
    """Fun\u00e7\u00e3o principal"""
    checker = FlowBalanceChecker()

    # Argumentos da linha de comando
    if len(sys.argv) > 1:
        address = sys.argv[1]
        network = sys.argv[2] if len(sys.argv) > 2 else 'mainnet'
    else:
        # Usa vari\u00e1veis de ambiente ou valores padr\u00e3o
        from dotenv import load_dotenv
        load_dotenv()

        address = os.getenv('FLOW_ACCOUNT_ADDRESS', '')
        network = os.getenv('FLOW_NETWORK', 'mainnet')

        if not address:
            print("\u274c Nenhum endere\u00e7o fornecido!")
            print("\nUso:")
            print("  python3 flow_balance_checker.py <endere\u00e7o> [network]")
            print("\nExemplos:")
            print("  python3 flow_balance_checker.py 0x1654653399040a61")
            print("  python3 flow_balance_checker.py 0x01cf0e2f2f715450 testnet")
            sys.exit(1)

    # Verifica o saldo
    success = checker.display_account_info(address, network)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()