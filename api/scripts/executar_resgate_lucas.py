#!/usr/bin/env python3
"""
Script para executar o resgate do Lucas Montano com presente de 5.0 FLOW
Isso vai REALMENTE debitar 5.0 FLOW da conta do Diego na testnet!
"""

import subprocess
import json

def executar_resgate_lucas():
    """
    Executa a transação de resgate com presente de 5.0 FLOW REAL
    """

    print("🏄 RESGATANDO LUCAS MONTANO COM 5.0 FLOW DE PRESENTE")
    print("="*50)
    print("⚠️  ATENÇÃO: Isso vai DEBITAR 5.0 FLOW REAL da testnet!")
    print("💰 Conta do Diego: 0x36395f9dde50ea27")
    print("="*50)

    # Comando para executar a transação
    cmd = [
        "flow", "transactions", "send",
        "scripts/resgatar_surfista_com_presente.cdc",
        "Lucas Montano",  # Nome do surfista
        "5.0",           # Presente de 5.0 FLOW (REAL!)
        "--network", "testnet",
        "--signer", "testnet-account"
    ]

    print("\n🚀 Executando transação na testnet...")
    print(f"Comando: {' '.join(cmd)}")

    try:
        # Executar transação
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/2a/Desktop/neo4j-agent-flow/api"
        )

        if result.returncode == 0:
            print("\n✅ SUCESSO! Transação executada!")
            print(result.stdout)

            # Parse do resultado para pegar o ID da transação
            for line in result.stdout.split('\n'):
                if 'Transaction ID' in line or 'transaction' in line.lower():
                    print(f"\n🔍 {line}")

            print("\n💰 FLUXO DO FLOW:")
            print("1. Diego tinha ~101,000 FLOW")
            print("2. Debitou 5.0 FLOW REAL da conta")
            print("3. FLOW foi para o Tesouro Protegido")
            print("4. Lucas pode usar esse FLOW para aprender!")
            print("5. Se descobrir a senha (SURF2024), ganha tudo!")

        else:
            print("\n❌ ERRO na transação!")
            print(result.stderr)

    except Exception as e:
        print(f"\n❌ Erro ao executar: {e}")

    print("\n" + "="*50)
    print("🔍 Para verificar o saldo atualizado, execute:")
    print("   python3 check_flow_balance_testnet.py")
    print("\n💡 Para verificar o Tesouro:")
    print("   flow scripts execute scripts/verificar_tesouro.cdc 0x25f823e2a115b2dc")

if __name__ == "__main__":
    executar_resgate_lucas()