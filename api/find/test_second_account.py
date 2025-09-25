#!/usr/bin/env python3
"""
🔍 TESTAR SEGUNDA CONTA COM NOVA CHAVE
"""

import subprocess
import json
import time

# Nova conta fornecida
ACCOUNT = "0x36395f9dde50ea27"
PRIVATE_KEY = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"
EVM_ADDRESS = "0x000000000000000000000002251fafd52a6b460c"

print("🔍 TESTANDO NOVA CONTA FLOW")
print("=" * 60)
print(f"📝 Conta: {ACCOUNT}")
print(f"🔑 Chave Privada: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")
print(f"🌐 EVM Address: {EVM_ADDRESS}")

# 1. Verificar conta na testnet
print("\n1️⃣ VERIFICANDO CONTA NA TESTNET:")
cmd = f"flow accounts get {ACCOUNT} --network testnet -o json 2>/dev/null"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    try:
        data = json.loads(result.stdout)
        balance = data.get('balance', '0')
        keys = data.get('keys', [])
        print(f"   ✅ Conta encontrada!")
        print(f"   💰 Saldo: {balance} FLOW")
        if keys:
            print(f"   🔓 Chave pública: {keys[0][:32]}...")
    except:
        print(f"   ❌ Erro ao processar resposta")
else:
    print(f"   ❌ Conta não encontrada na testnet")

# 2. Criar flow.json com a nova conta
print("\n2️⃣ CONFIGURANDO FLOW.JSON:")
flow_config = {
    "networks": {
        "testnet": "access.devnet.nodes.onflow.org:9000"
    },
    "accounts": {
        "test-account": {
            "address": ACCOUNT.replace("0x", ""),
            "key": PRIVATE_KEY
        }
    }
}

with open("flow.json", "w") as f:
    json.dump(flow_config, f, indent=2)
print(f"   ✅ Configuração criada")

# 3. Testar transação simples
print("\n3️⃣ TESTANDO ASSINATURA COM TRANSAÇÃO:")
test_tx = """
transaction {
    prepare(signer: auth(Storage) &Account) {
        log("Teste de assinatura com nova conta")
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

print(f"   Enviando transação de teste...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

if "SEALED" in result.stdout:
    if "Transaction Error" in result.stdout:
        if "signature is not valid" in result.stdout:
            print(f"   ❌ ERRO: Assinatura inválida - chave não corresponde!")
        else:
            print(f"   ❌ Outro erro na transação")
    else:
        print(f"   ✅ SUCESSO! Transação assinada corretamente!")
        print(f"   🎉 Esta conta e chave FUNCIONAM!")

        # Extrair TX ID
        import re
        tx_match = re.search(r'ID\s+([a-f0-9]{64})', result.stdout)
        if tx_match:
            tx_id = tx_match.group(1)
            print(f"   📝 TX ID: {tx_id}")
else:
    print(f"   ❌ Erro ao enviar transação")
    if result.stderr:
        print(f"   Erro: {result.stderr[:200]}")

# 4. Se funcionar, sugerir atualização do .env
print("\n4️⃣ PRÓXIMOS PASSOS:")
print("   Se a transação funcionou, atualize o .env:")
print(f"   FLOW_ACCOUNT_ADDRESS={ACCOUNT}")
print(f"   FLOW_PRIVATE_KEY={PRIVATE_KEY}")

# Limpar arquivos
import os
for f in ["flow.json", "test.cdc"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 60)