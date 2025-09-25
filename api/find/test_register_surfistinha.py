#!/usr/bin/env python3
"""
🏄 REGISTRAR SURFISTINHA.FIND NA TESTNET
Usando a conta e chave que funcionam
"""

import subprocess
import json
import time
import sys

# Conta que funciona (testada e validada)
ACCOUNT = "0x36395f9dde50ea27"
PRIVATE_KEY = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"
NAME_TO_REGISTER = "surfistinha"

print("🏄 REGISTRANDO SURFISTINHA.FIND")
print("=" * 60)
print(f"📝 Nome: {NAME_TO_REGISTER}.find")
print(f"👤 Conta: {ACCOUNT}")
print(f"🔑 Chave: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")

# 1. Verificar saldo
print("\n1️⃣ VERIFICANDO SALDO:")
cmd = f"flow accounts get {ACCOUNT} --network testnet -o json 2>/dev/null"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    try:
        data = json.loads(result.stdout)
        balance = float(data.get('balance', '0'))
        print(f"   💰 Saldo: {balance:.2f} FLOW")

        if balance < 10:
            print(f"   ❌ Saldo insuficiente! Precisa de pelo menos 10 FLOW")
            sys.exit(1)
    except:
        print(f"   ❌ Erro ao verificar saldo")
        sys.exit(1)
else:
    print(f"   ❌ Erro ao acessar conta")
    sys.exit(1)

# 2. Criar flow.json
print("\n2️⃣ CONFIGURANDO FLOW.JSON:")
flow_config = {
    "networks": {
        "testnet": "access.devnet.nodes.onflow.org:9000"
    },
    "accounts": {
        "surfistinha-account": {
            "address": ACCOUNT.replace("0x", ""),
            "key": PRIVATE_KEY
        }
    }
}

with open("flow.json", "w") as f:
    json.dump(flow_config, f, indent=2)
print(f"   ✅ Configuração criada")

# 3. Criar script Cadence para registro
print("\n3️⃣ CRIANDO SCRIPT DE REGISTRO:")
register_script = """
import FIND from 0x35717efbbce11c74

transaction(name: String) {

    let account: auth(Storage, Capabilities) &Account

    prepare(signer: auth(Storage, Capabilities) &Account) {
        self.account = signer
    }

    execute {
        // Registrar nome .find
        FIND.register(name: name, account: self.account.address)

        // Log para confirmar
        log("Registrando nome: ".concat(name).concat(".find"))
        log("Para conta: ".concat(self.account.address.toString()))
    }
}
"""

with open("register_find.cdc", "w") as f:
    f.write(register_script)
print(f"   ✅ Script Cadence criado")

# 4. Enviar transação
print(f"\n4️⃣ ENVIANDO TRANSAÇÃO DE REGISTRO:")
print(f"   🎯 Registrando: {NAME_TO_REGISTER}.find")

cmd = [
    "flow", "transactions", "send",
    "register_find.cdc",
    f"String:{NAME_TO_REGISTER}",
    "--network", "testnet",
    "--signer", "surfistinha-account",
    "--gas-limit", "9999",
    "-y"
]

print(f"   ⏳ Enviando transação...")
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    # Analisar resultado
    if "SEALED" in result.stdout:
        if "Transaction Error" in result.stdout:
            print(f"   ❌ Erro na transação!")

            # Verificar diferentes erros
            if "already registered" in result.stdout.lower():
                print(f"   ⚠️ O nome '{NAME_TO_REGISTER}.find' já está registrado!")
            elif "insufficient" in result.stdout.lower():
                print(f"   ⚠️ Saldo insuficiente para registro")
            elif "signature" in result.stdout.lower():
                print(f"   ⚠️ Erro de assinatura - chave inválida")
            else:
                print(f"   ⚠️ Erro desconhecido")
                print(f"\nDetalhes: {result.stdout[:500]}")
        else:
            print(f"   ✅ SUCESSO! Nome registrado!")
            print(f"   🎉 {NAME_TO_REGISTER}.find agora pertence a {ACCOUNT}")

            # Extrair TX ID
            import re
            tx_match = re.search(r'ID\s+([a-f0-9]{64})', result.stdout)
            if tx_match:
                tx_id = tx_match.group(1)
                print(f"   📝 TX ID: {tx_id}")
                print(f"   🔗 Ver em: https://testnet.flowdiver.io/tx/{tx_id}")
    else:
        print(f"   ❌ Transação não foi selada")
        if result.stderr:
            print(f"   Erro: {result.stderr[:300]}")

except subprocess.TimeoutExpired:
    print(f"   ⏱️ Timeout - transação demorou muito")
except Exception as e:
    print(f"   ❌ Erro inesperado: {e}")

# 5. Verificar se o nome foi registrado
print(f"\n5️⃣ VERIFICANDO REGISTRO:")
check_script = f"""
import FIND from 0x35717efbbce11c74

pub fun main(name: String): Address? {{
    return FIND.lookupAddress(name)
}}
"""

with open("check_find.cdc", "w") as f:
    f.write(check_script)

cmd = [
    "flow", "scripts", "execute",
    "check_find.cdc",
    f"String:{NAME_TO_REGISTER}",
    "--network", "testnet",
    "-o", "json"
]

time.sleep(2)  # Aguardar propagação
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    try:
        data = json.loads(result.stdout)
        if data and data != "null":
            print(f"   ✅ CONFIRMADO! {NAME_TO_REGISTER}.find → {data}")
        else:
            print(f"   ⚠️ Nome ainda não aparece no registro")
    except:
        print(f"   ⚠️ Não foi possível verificar")

# 6. Limpar arquivos temporários
print(f"\n6️⃣ LIMPANDO ARQUIVOS:")
import os
for f in ["flow.json", "register_find.cdc", "check_find.cdc"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"   🗑️ {f} removido")

print("\n" + "=" * 60)
print("🏁 PROCESSO CONCLUÍDO!")
print("=" * 60)