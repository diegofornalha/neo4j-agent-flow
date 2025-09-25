#!/usr/bin/env python3
"""
🔑 GERAR NOVO PAR DE CHAVES E INSTRUÇÕES PARA CRIAR CONTA
"""

import subprocess
import json

print("🔑 GERANDO NOVO PAR DE CHAVES FLOW")
print("=" * 60)

# Gerar novo par de chaves
result = subprocess.run(["flow", "keys", "generate"], capture_output=True, text=True)

if result.returncode == 0:
    output = result.stdout
    print(output)

    # Extrair chaves
    lines = output.split('\n')
    private_key = None
    public_key = None

    for line in lines:
        if "Private Key" in line:
            private_key = line.split()[-1]
        elif "Public Key" in line:
            public_key = line.split()[-1]

    if private_key and public_key:
        print("\n✅ CHAVES GERADAS COM SUCESSO!")
        print(f"\n🔐 PRIVATE KEY: {private_key}")
        print(f"🔓 PUBLIC KEY: {public_key}")

        print("\n📝 PRÓXIMOS PASSOS:")
        print("=" * 60)
        print("1. CRIAR CONTA NA TESTNET:")
        print("   - Acesse: https://testnet-faucet.onflow.org/")
        print(f"   - Cole a PUBLIC KEY: {public_key}")
        print("   - Escolha: ECDSA_P256 / SHA2_256")
        print("   - Clique em 'Create Account'")
        print("   - Anote o endereço da conta (0x...)")

        print("\n2. ATUALIZAR O .env:")
        print(f"   FLOW_ACCOUNT_ADDRESS=0x[NOVO_ENDERECO]")
        print(f"   FLOW_PRIVATE_KEY={private_key}")

        print("\n3. TESTAR:")
        print("   python3 test_new_account.py")

        # Salvar em arquivo
        config = {
            "private_key": private_key,
            "public_key": public_key,
            "instructions": "Use the faucet to create account, then update .env"
        }

        with open("new_keys.json", "w") as f:
            json.dump(config, f, indent=2)

        print("\n💾 Chaves salvas em: new_keys.json")
        print("⚠️  GUARDE A PRIVATE KEY COM SEGURANÇA!")

else:
    print("❌ Erro ao gerar chaves")
    print(result.stderr)