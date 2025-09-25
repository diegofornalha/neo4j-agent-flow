#!/usr/bin/env python3
"""
Testar transação simples para confirmar que tudo ainda funciona
"""

import subprocess
import json
import os
from datetime import datetime

# Credenciais
ACCOUNT = "0x36395f9dde50ea27"
PRIVATE_KEY = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"

print("🧪 TESTE SIMPLES DE TRANSAÇÃO")
print("=" * 60)

# 1. Verificar saldo antes
print("\n💰 Verificando saldo...")
cmd = f"flow accounts get {ACCOUNT} --network testnet 2>/dev/null | grep Balance"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(f"   {result.stdout.strip()}")

# 2. Criar flow.json
flow_config = {
    "networks": {
        "testnet": "access.devnet.nodes.onflow.org:9000"
    },
    "accounts": {
        "main": {
            "address": ACCOUNT.replace("0x", ""),
            "key": {
                "type": "hex",
                "index": 0,
                "signatureAlgorithm": "ECDSA_secp256k1",
                "hashAlgorithm": "SHA2_256",
                "privateKey": PRIVATE_KEY
            }
        }
    }
}

with open("flow.json", "w") as f:
    json.dump(flow_config, f, indent=2)

# 3. Transação simples (como a que funcionou antes)
test_tx = f"""
transaction {{
    prepare(signer: auth(Storage) &Account) {{
        log("✅ Teste às {datetime.now().strftime('%H:%M:%S')}")
        log("Conta: ".concat(signer.address.toString()))
        log("Transação funcionando perfeitamente!")
    }}
}}
"""

with open("test.cdc", "w") as f:
    f.write(test_tx)

# 4. Enviar
print("\n📤 Enviando transação de teste...")
cmd = ["flow", "transactions", "send", "test.cdc", "--network", "testnet", "--signer", "main", "-y"]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

if "SEALED" in result.stdout:
    print("✅ TRANSAÇÃO FUNCIONOU!")

    # Extrair TX ID
    import re
    tx_match = re.search(r'ID\s+([a-f0-9]{64})', result.stdout)
    if tx_match:
        tx_id = tx_match.group(1)
        print(f"\n📝 Transaction ID: {tx_id}")
        print(f"🔗 Ver: https://testnet.flowscan.io/tx/{tx_id}")
else:
    print("❌ Erro na transação")
    print(result.stdout)

# Limpar
for f in ["flow.json", "test.cdc"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 60)