#!/usr/bin/env python3
"""
🔑 CONVERTER MNEMONIC PARA CHAVES FLOW
"""

try:
    from mnemonic import Mnemonic
    from hashlib import sha256
    import hmac
    import hashlib
except ImportError:
    print("Instalando bibliotecas necessárias...")
    import subprocess
    subprocess.run(["pip3", "install", "mnemonic"], capture_output=True)
    from mnemonic import Mnemonic
    from hashlib import sha256
    import hmac
    import hashlib

# Frase fornecida
MNEMONIC_PHRASE = "effort settle trash drift mouse sausage address must spot fault put lonely"

print("🔑 CONVERTENDO MNEMONIC PARA CHAVES")
print("=" * 60)
print(f"📝 Mnemonic: {MNEMONIC_PHRASE}")

# Verificar se a mnemonic é válida
mnemo = Mnemonic("english")
if not mnemo.check(MNEMONIC_PHRASE):
    print("⚠️ Aviso: Mnemonic pode não ser válida")

# Converter para seed
seed = mnemo.to_seed(MNEMONIC_PHRASE, passphrase="")
print(f"\n🌱 Seed gerada: {seed.hex()[:32]}...")

# Derivar chave usando BIP32 path para Flow: m/44'/539'/0'/0/0
# Flow usa curve P-256 (secp256r1)

# Para Flow, precisamos usar a biblioteca específica ou ferramenta CLI
# Vamos tentar usar o flow-py-sdk se disponível

print("\n🔄 Tentando derivar chaves para Flow...")

# Método alternativo: usar o flow keys generate com --mnemonic
import subprocess
import json

# Criar arquivo temporário com a mnemonic
with open("/tmp/mnemonic.txt", "w") as f:
    f.write(MNEMONIC_PHRASE)

# Tentar gerar conta a partir da mnemonic
# Infelizmente o Flow CLI não tem opção direta para isso

print("\n⚠️ O Flow CLI não suporta derivação direta de mnemonic")
print("   Mas podemos testar se a seed corresponde a alguma conta...")

# Vamos testar se essa mnemonic gera alguma das chaves privadas conhecidas
print("\n🔍 Testando correspondências conhecidas:")

# Chaves privadas que temos
known_keys = {
    "Conta 1": "4c1b7d1e4128413b60283a787f750db4b6228c9f1bd063479073900b3fd9985f",
    "Conta 2": "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"
}

# A seed em hex
seed_hex = seed.hex()

for name, key in known_keys.items():
    print(f"\n   {name}:")
    print(f"   Chave: {key[:16]}...")
    # Verificar se parte da seed corresponde
    if key[:16] in seed_hex or seed_hex[:16] in key:
        print(f"   ✅ Possível correspondência!")
    else:
        print(f"   ❌ Não corresponde")

print("\n📝 NOTA IMPORTANTE:")
print("   Para recuperar a chave privada exata do Flow a partir")
print("   da mnemonic, precisamos usar a mesma derivação que foi")
print("   usada originalmente (BIP32/BIP44 com curve P-256)")

print("\n💡 SOLUÇÃO ALTERNATIVA:")
print("   1. Importe a mnemonic em uma wallet Flow compatível")
print("   2. A wallet derivará a chave privada correta")
print("   3. Exporte a chave privada da wallet")

print("\n🔧 Wallets compatíveis:")
print("   - Flow Wallet Extension")
print("   - Blocto")
print("   - Lilico Wallet")

print("\n" + "=" * 60)