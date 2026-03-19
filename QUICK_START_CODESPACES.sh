#!/bin/bash

# GISBIM Online v2.0 - Quick Start Script para Codespaces
# Execute este script no terminal do Codespaces

echo "🚀 GISBIM Online v2.0 - Setup Rápido"
echo "======================================"
echo ""

# Passo 1: Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Passo 2: Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Passo 3: Verificar sintaxe
echo "✅ Verificando sintaxe dos arquivos Python..."
python3 -m py_compile backend/spatial.py backend/app.py
if [ $? -eq 0 ]; then
    echo "✓ Sem erros de sintaxe!"
else
    echo "✗ Erros encontrados!"
    exit 1
fi

# Passo 4: Exibir informações
echo ""
echo "✨ Setup Concluído!"
echo ""
echo "Para iniciar a aplicação, execute:"
echo "  cd backend"
echo "  python app.py"
echo ""
echo "A aplicação estará disponível em: http://localhost:5000"
echo ""
echo "Para testar os endpoints, abra outro terminal e execute:"
echo "  curl http://localhost:5000/health"
echo ""
echo "Documentação de API: API_ENDPOINTS.md"
echo "Guia completo: README_NOVO.md"
echo ""
