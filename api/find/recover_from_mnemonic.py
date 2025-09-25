#!/usr/bin/env python3
"""
🔑 RECUPERAR CHAVES A PARTIR DA FRASE DE SEGURANÇA
"""

import subprocess
import json

# Frase de segurança fornecida
MNEMONIC = "effort settle trash drift mouse sausage address must spot fault put lonely"

print("🔑 RECUPERANDO CHAVES DA FRASE DE SEGURANÇA")
print("=" * 60)
print(f"📝 Mnemonic: {MNEMONIC}")
print()

# Usar Flow CLI para derivar chaves da mnemonic
print("🔄 Derivando chaves...")

# Criar arquivo temporário com a mnemonic
with open("/tmp/mnemonic.txt", "w") as f:
    f.write(MNEMONIC)

# Comando para derivar chaves
# Flow CLI usa derivation path padrão: m/44'/539'/0'/0/0
cmd = f"echo '{MNEMONIC}' | flow keys derive"

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    output = result.stdout
    print(output)

    # Extrair informações
    lines = output.split('\n')
    private_key = None
    public_key = None

    for line in lines:
        if "Private Key" in line:
            parts = line.split()
            if len(parts) > 0:
                private_key = parts[-1]
        elif "Public Key" in line and "Public Key" in line:
            parts = line.split()
            if len(parts) > 0:
                public_key = parts[-1]

    if private_key and public_key:
        print("\n✅ CHAVES RECUPERADAS COM SUCESSO!")
        print(f"\n🔐 PRIVATE KEY: {private_key}")
        print(f"🔓 PUBLIC KEY: {public_key}")

        # Verificar se corresponde às contas conhecidas
        print("\n🔍 VERIFICANDO CORRESPONDÊNCIA COM CONTAS CONHECIDAS:")

        # Conta 1: 0x25f823e2a115b2dc
        print("\n   Conta 1: 0x25f823e2a115b2dc")
        cmd1 = "flow accounts get 0x25f823e2a115b2dc --network testnet -o json 2>/dev/null"
        result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
        if result1.returncode == 0:
            data = json.loads(result1.stdout)
            blockchain_key1 = data.get('keys', [''])[0][:64] if data.get('keys') else ''
            if public_key[:64] in blockchain_key1 or blockchain_key1 in public_key:
                print(f"   ✅ CORRESPONDE! Esta é a chave correta!")
            else:
                print(f"   ❌ Não corresponde")
                print(f"   Blockchain: {blockchain_key1[:32]}...")
                print(f"   Derivada:   {public_key[:32]}...")

        # Conta 2: 0x36395f9dde50ea27
        print("\n   Conta 2: 0x36395f9dde50ea27")
        cmd2 = "flow accounts get 0x36395f9dde50ea27 --network testnet -o json 2>/dev/null"
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        if result2.returncode == 0:
            data = json.loads(result2.stdout)
            blockchain_key2 = data.get('keys', [''])[0][:64] if data.get('keys') else ''
            if public_key[:64] in blockchain_key2 or blockchain_key2 in public_key:
                print(f"   ✅ CORRESPONDE! Esta é a chave correta!")
            else:
                print(f"   ❌ Não corresponde")
                print(f"   Blockchain: {blockchain_key2[:32]}...")
                print(f"   Derivada:   {public_key[:32]}...")

        # Salvar as chaves recuperadas
        recovered = {
            "mnemonic": MNEMONIC,
            "private_key": private_key,
            "public_key": public_key,
            "derivation_path": "m/44'/539'/0'/0/0"
        }

        with open("recovered_keys.json", "w") as f:
            json.dump(recovered, f, indent=2)

        print("\n💾 Chaves salvas em: recovered_keys.json")

        print("\n📋 SE CORRESPONDER A UMA CONTA, ATUALIZE O .ENV:")
        print(f"   FLOW_PRIVATE_KEY={private_key}")

    else:
        print("❌ Não foi possível extrair as chaves")
        print(output)

else:
    print("❌ Erro ao derivar chaves")
    print(result.stderr)

print("\n" + "=" * 60)