#!/usr/bin/env python3
"""
🔍 BUSCAR CONTA COM A NOVA CHAVE PÚBLICA
"""

import subprocess
import json

PUBLIC_KEY = "63f40b6701ead5d0ae370c808485094a9c30eb27cb337ecfdba0596f456295f112c96acb36cf23ea51c1db365c788179ac4aa89d535bfddf863588dbc907961e"
PRIVATE_KEY = "c4bbb40386ff9c2c6f3bd84a8b43491f96163ed55ce4c291c3cd625b1a6bddf3"

print("🔍 PROCURANDO CONTA COM A NOVA CHAVE")
print("=" * 60)
print(f"🔓 Chave pública: {PUBLIC_KEY[:20]}...{PUBLIC_KEY[-10:]}")

# Lista de possíveis contas para verificar (baseado no que vimos antes)
possible_accounts = [
    "0x25f823e2a115b2dc",  # Conta principal do projeto
    "0x36395f9dde50ea27",  # Segunda conta
]

found = False

for account in possible_accounts:
    cmd = f"flow accounts get {account} --network testnet -o json 2>/dev/null"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            keys = data.get('keys', [])

            if keys:
                # Verificar se a chave pública corresponde
                account_public_key = keys[0]
                if PUBLIC_KEY in account_public_key or account_public_key in PUBLIC_KEY:
                    print(f"\n✅ CONTA ENCONTRADA: {account}")
                    print(f"   💰 Saldo: {data.get('balance', '0')} FLOW")
                    print(f"   🔑 Esta chave privada funciona para esta conta!")
                    found = True
                    break
        except:
            pass

if not found:
    print(f"\n⚠️ Nenhuma conta existente usa esta chave pública")
    print(f"   Você precisa criar uma nova conta usando o faucet")
    print(f"   Ou usar um par de chaves diferente")

print("\n" + "=" * 60)