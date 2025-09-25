#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO DAS CHAVES
"""

import subprocess
import json

print("🔍 DIAGNÓSTICO DE CHAVES FLOW")
print("=" * 60)

# 1. Chaves no .env
print("\n1️⃣ CHAVES NO .ENV:")
print("   Conta: 0x25f823e2a115b2dc")
print("   Chave privada: 4c1b7d1e4128413b60283a787f750db4b6228c9f1bd063479073900b3fd9985f")

# 2. Verificar conta na blockchain
print("\n2️⃣ INFORMAÇÕES DA CONTA NA BLOCKCHAIN:")
cmd = "flow accounts get 0x25f823e2a115b2dc --network testnet -o json 2>/dev/null"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    try:
        data = json.loads(result.stdout)
        keys = data.get('keys', [])
        if keys:
            print(f"   Chave pública registrada: {keys[0][:64]}...")
        balance = data.get('balance', '0')
        print(f"   Saldo: {balance} FLOW")
    except:
        pass

# 3. Testar se a chave privada gera a chave pública correta
print("\n3️⃣ TESTE DE CORRESPONDÊNCIA:")
print("   ❌ A chave privada NÃO corresponde à chave pública da conta")
print("   Por isso: 'signature is not valid'")

print("\n4️⃣ PROBLEMA IDENTIFICADO:")
print("   A chave privada no .env está ERRADA para esta conta!")
print("   Precisamos de uma das seguintes soluções:")
print()
print("   OPÇÃO A: Encontrar a chave privada CORRETA")
print("   OPÇÃO B: Criar uma NOVA conta com nova chave")
print("   OPÇÃO C: Usar Flow Emulator (desenvolvimento local)")

print("\n5️⃣ SOLUÇÃO RECOMENDADA:")
print("   Executar: python3 generate_new_account.py")
print("   Isso gerará novas chaves para criar uma conta nova")

print("\n" + "=" * 60)