#!/usr/bin/env python3
"""
🎯 REGISTRAR NOME .FIND NA TESTNET - REAL!
Com as credenciais corretas funcionando
"""

import subprocess
import json
import os
from datetime import datetime

# Credenciais CONFIRMADAS funcionando
ACCOUNT = "0x36395f9dde50ea27"
PRIVATE_KEY = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"

print("🚀 REGISTRO REAL DE NOME .FIND NA TESTNET")
print("=" * 60)
print(f"💰 Conta: {ACCOUNT}")
print(f"🔑 Chave: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")

# 1. Nome único para registrar
timestamp = datetime.now().strftime("%H%M%S")
nome_base = "surfista"
nome_completo = f"{nome_base}{timestamp}"

print(f"\n📝 Nome a registrar: {nome_completo}.find")

# 2. Criar flow.json com configuração correta
print("\n⚙️ Configurando flow.json...")

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
                "signatureAlgorithm": "ECDSA_secp256k1",  # CRÍTICO!
                "hashAlgorithm": "SHA2_256",
                "privateKey": PRIVATE_KEY
            }
        }
    }
}

config_file = "flow.json"
with open(config_file, "w") as f:
    json.dump(flow_config, f, indent=2)

print("   ✅ flow.json configurado com ECDSA_secp256k1")

# 3. Transação Cadence para registrar nome .find
print("\n📄 Criando transação Cadence...")

# Transação simplificada para teste inicial
register_tx = f"""
import FIND from 0x35717efbbce11c74
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

transaction(name: String, amount: UFix64) {{
    let vault: @FungibleToken.Vault

    prepare(account: auth(Storage) &Account) {{
        // Pegar referência ao vault de Flow tokens
        let vaultRef = account.storage.borrow<&FlowToken.Vault>(
            from: /storage/flowTokenVault
        ) ?? panic("Could not borrow Flow token vault")

        // Sacar o valor para pagar pelo nome
        self.vault <- vaultRef.withdraw(amount: amount)

        log("Preparando registro de: ".concat(name))
    }}

    execute {{
        // Registrar o nome no FIND
        FIND.bid(name: name, vault: <- self.vault)
        log("✅ Nome registrado: ".concat(name).concat(".find"))
    }}
}}
"""

tx_file = "register_find_name.cdc"
with open(tx_file, "w") as f:
    f.write(register_tx)

print("   ✅ Transação criada")

# 4. Enviar transação
print(f"\n🚀 Enviando transação para registrar '{nome_completo}.find'...")
print("   Custo estimado: 5-10 FLOW")

cmd = [
    "flow", "transactions", "send",
    tx_file,
    nome_completo,  # nome a registrar
    "5.0",          # valor em FLOW (começar com 5)
    "--network", "testnet",
    "--signer", "main",
    "-y"
]

print(f"\n   Comando: {' '.join(cmd)}")
print("\n   Executando...")

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if "SEALED" in result.stdout:
        print("\n🎉 SUCESSO! TRANSAÇÃO ENVIADA!")

        # Extrair Transaction ID
        import re
        tx_match = re.search(r'ID\s+([a-f0-9]{64})', result.stdout)
        if tx_match:
            tx_id = tx_match.group(1)
            print(f"\n📝 Transaction ID: {tx_id}")
            print(f"🔗 Ver na blockchain: https://testnet.flowscan.io/tx/{tx_id}")
            print(f"\n✅ Nome '{nome_completo}.find' deve estar registrado!")
            print("   Aguarde alguns segundos para confirmação na blockchain")

            # Salvar informações
            with open("registro_sucesso.txt", "w") as f:
                f.write(f"Nome registrado: {nome_completo}.find\n")
                f.write(f"Transaction ID: {tx_id}\n")
                f.write(f"Conta: {ACCOUNT}\n")
                f.write(f"Data: {datetime.now()}\n")
                f.write(f"URL: https://testnet.flowscan.io/tx/{tx_id}\n")

            print(f"\n📄 Detalhes salvos em 'registro_sucesso.txt'")
        else:
            print("\n⚠️ Transação enviada mas não consegui extrair o ID")
            print(f"Output: {result.stdout}")
    else:
        print("\n❌ Erro ao registrar nome")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

except subprocess.TimeoutExpired:
    print("\n⏱️ Timeout na transação (30s)")
except Exception as e:
    print(f"\n❌ Erro: {e}")

# 5. Verificar o nome (opcional)
print("\n🔍 Para verificar se o nome foi registrado:")
print(f"   1. Acesse: https://testnet.flowscan.io/account/{ACCOUNT}")
print(f"   2. Ou tente resolver: {nome_completo}.find")

# Limpar arquivos temporários
for f in [config_file, tx_file]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 60)
print("🏁 PROCESSO CONCLUÍDO!")
print("=" * 60)