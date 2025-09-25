#!/usr/bin/env python3
"""
🔧 TESTAR CHAVE COM DIFERENTES FORMATOS
"""

import subprocess
import json
import os

ACCOUNT = "0x36395f9dde50ea27"
PRIVATE_KEY = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"

print("🔧 TESTANDO FORMATOS DE CHAVE")
print("=" * 60)

# Teste 1: Com key como objeto detalhado
print("\n1️⃣ TESTE COM FORMATO DETALHADO:")
flow_config = {
    "networks": {
        "testnet": "access.devnet.nodes.onflow.org:9000"
    },
    "accounts": {
        "test-account": {
            "address": ACCOUNT.replace("0x", ""),
            "key": {
                "type": "hex",
                "index": 0,
                "signatureAlgorithm": "ECDSA_P256",
                "hashAlgorithm": "SHA3_256",
                "privateKey": PRIVATE_KEY
            }
        }
    }
}

with open("flow.json", "w") as f:
    json.dump(flow_config, f, indent=2)

# Criar transação simples
test_tx = """
transaction {
    prepare(signer: auth(Storage) &Account) {
        log("Teste com formato detalhado")
        log(signer.address)
    }
}
"""

with open("test.cdc", "w") as f:
    f.write(test_tx)

# Enviar transação
cmd = [
    "flow", "transactions", "send",
    "test.cdc",
    "--network", "testnet",
    "--signer", "test-account",
    "-y"
]

print(f"   Enviando transação...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

if "SEALED" in result.stdout:
    if "signature is not valid" in result.stdout:
        print(f"   ❌ Formato detalhado: Assinatura inválida")
    elif "Transaction Error" not in result.stdout:
        print(f"   ✅ FORMATO DETALHADO FUNCIONA!")
    else:
        print(f"   ❌ Outro erro")
else:
    print(f"   ❌ Não selada: {result.stderr[:100]}")

# Teste 2: Com prefixo 0x na chave
print("\n2️⃣ TESTE COM PREFIXO 0x:")
flow_config = {
    "networks": {
        "testnet": "access.devnet.nodes.onflow.org:9000"
    },
    "accounts": {
        "test-account": {
            "address": ACCOUNT.replace("0x", ""),
            "key": f"0x{PRIVATE_KEY}"
        }
    }
}

with open("flow.json", "w") as f:
    json.dump(flow_config, f, indent=2)

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

if "SEALED" in result.stdout:
    if "signature is not valid" in result.stdout:
        print(f"   ❌ Com prefixo 0x: Assinatura inválida")
    elif "Transaction Error" not in result.stdout:
        print(f"   ✅ PREFIXO 0x FUNCIONA!")
    else:
        print(f"   ❌ Outro erro")
else:
    print(f"   ❌ Não selada")

# Limpar
for f in ["flow.json", "test.cdc"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 60)