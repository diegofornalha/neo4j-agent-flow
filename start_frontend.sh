#!/bin/bash
# Script para iniciar o frontend

cd /Users/2a/Desktop/neo4j-agent-flow/chat
echo "============================================================"
echo "🔧 HACKATHON FLOW BLOCKCHAIN AGENTS - FRONTEND"
echo "============================================================"
echo "📡 Iniciando servidor na porta 3001..."
echo "🔗 Acesse: http://localhost:3001"
echo "============================================================"

# Tenta com Python 3
python3 -m http.server 3001 2>/dev/null || python -m http.server 3001