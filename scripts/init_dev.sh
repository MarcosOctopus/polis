#!/bin/bash
# Inicializa o ambiente de desenvolvimento do backend Polis
# Uso: bash scripts/init_dev.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Ativando virtualenv..."
source .venv/bin/activate

echo "==> Instalando dependencias..."
uv pip install --quiet \
    aiosqlite \
    fastapi \
    uvicorn \
    sqlalchemy \
    python-jose \
    "passlib[bcrypt]" \
    python-multipart \
    python-dotenv \
    httpx

echo "==> Verificando .env..."
if [ ! -f .env ]; then
    echo "Criando .env com configuracao SQLite..."
    printf 'POLIS_DATABASE_URL=sqlite+aiosqlite:///./polis.db\nPOLIS_ENVIRONMENT=development\nPOLIS_DEBUG=true\nPOLIS_JWT_SECRET_KEY=polis_...\n' > .env
fi

echo "==> Iniciando servidor de desenvolvimento..."
cd src
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
