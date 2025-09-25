"""
Configurações do Flow Name Service (FNS)
"""

import os
from dataclasses import dataclass

@dataclass
class FNSNetworkConfig:
    """Configurações de rede para FNS"""
    # Contratos
    TESTNET_CONTRACT = os.getenv("FNS_TESTNET_CONTRACT", "0x35717efbbce11c74")
    MAINNET_CONTRACT = os.getenv("FNS_MAINNET_CONTRACT", "0x097bafa4e0b48eef")

    # Access Nodes
    TESTNET_ACCESS_NODE = os.getenv("FLOW_TESTNET_NODE", "access.devnet.nodes.onflow.org")
    TESTNET_PORT = os.getenv("FLOW_TESTNET_PORT", "9000")
    MAINNET_ACCESS_NODE = os.getenv("FLOW_MAINNET_NODE", "access.mainnet.nodes.onflow.org")
    MAINNET_PORT = os.getenv("FLOW_MAINNET_PORT", "9000")

    # APIs
    FIND_API_URL = os.getenv("FIND_API_URL", "https://api.find.xyz")
    FAUCET_URL = os.getenv("FLOW_FAUCET_URL", "https://faucet.flow.com/fund-account")

    # Network
    DEFAULT_NETWORK = os.getenv("FNS_NETWORK", "testnet")

    # Cache
    CACHE_TTL_SECONDS = int(os.getenv("FNS_CACHE_TTL", "300"))  # 5 minutos

    # Quiz
    QUIZ_PASS_SCORE = int(os.getenv("FNS_QUIZ_PASS_SCORE", "80"))
    QUIZ_MASTER_SCORE = int(os.getenv("FNS_QUIZ_MASTER_SCORE", "95"))

# Preços por tier
TIER_PRICES = {
    "testnet": {
        "exclusive": 50.0,   # ≤3 chars
        "premium": 15.0,     # 4-5 chars
        "standard": 5.0      # ≥6 chars
    },
    "mainnet": {
        "exclusive": 500.0,
        "premium": 150.0,
        "standard": 50.0
    }
}

# Badges e benefícios
BADGES = {
    "flow-expert": {
        "min_score": 80,
        "discount": 0.2,  # 20% desconto
        "benefits": ["Nomes premium", "Suporte prioritário"]
    },
    "flow-master": {
        "min_score": 95,
        "discount": 0.5,  # 50% desconto
        "benefits": ["Nomes exclusivos", "Early access", "NFT especial"]
    }
}

# Validação de nomes
NAME_RULES = {
    "min_length": 3,
    "max_length": 16,
    "pattern": r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$',
    "reserved_names": ["admin", "root", "system", "flow", "find"]
}