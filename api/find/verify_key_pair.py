#!/usr/bin/env python3
"""
🔑 VERIFICAR SE A CHAVE PRIVADA CORRESPONDE À PÚBLICA
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib

PRIVATE_KEY_HEX = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"
EXPECTED_PUBLIC = "5a4579fec91240793b986203fa25cfbbfd71be1cc54c73ae20e4fdde6f07061a1b2162f7df4acaca118c6b152ca718fc2cbf304ef8625bc6c24143d63c5933d7"

print("🔑 VERIFICANDO PAR DE CHAVES")
print("=" * 60)

try:
    # Converter hex para bytes
    private_key_bytes = bytes.fromhex(PRIVATE_KEY_HEX)

    # Criar chave privada P-256
    private_key = ec.derive_private_key(
        int.from_bytes(private_key_bytes, 'big'),
        ec.SECP256R1(),
        default_backend()
    )

    # Obter chave pública
    public_key = private_key.public_key()

    # Serializar chave pública em formato não comprimido
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # Converter para hex (removendo o primeiro byte 0x04 que indica não comprimido)
    public_key_hex = public_key_bytes[1:].hex()

    print(f"📝 Chave privada: {PRIVATE_KEY_HEX[:10]}...{PRIVATE_KEY_HEX[-6:]}")
    print(f"🔓 Chave pública gerada: {public_key_hex[:10]}...{public_key_hex[-6:]}")
    print(f"🎯 Chave pública esperada: {EXPECTED_PUBLIC[:10]}...{EXPECTED_PUBLIC[-6:]}")

    if public_key_hex == EXPECTED_PUBLIC:
        print(f"\n✅ AS CHAVES CORRESPONDEM!")
    else:
        print(f"\n❌ AS CHAVES NÃO CORRESPONDEM!")
        print(f"   A chave privada fornecida NÃO gera a chave pública da conta!")

except Exception as e:
    print(f"❌ Erro ao processar chaves: {e}")

print("\n" + "=" * 60)