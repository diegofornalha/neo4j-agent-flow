"""
Flow Name Service (FNS) - Find Module
Sistema completo para registro e gerenciamento de nomes .find
"""

from .fns_integration import (
    FindNameService,
    FNSConfig,
    NameTier,
    setup_fns_endpoints
)

__all__ = [
    'FindNameService',
    'FNSConfig',
    'NameTier',
    'setup_fns_endpoints'
]

__version__ = '1.0.0'