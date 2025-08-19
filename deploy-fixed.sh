#!/bin/bash

# Configurar variables
export GITHUB_TOKEN="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"
REPO_DIR="/home/user/proyecto-nitro"

cd $REPO_DIR

# Corregir el error en requirements.txt
if [ -f "api-dashboard/dashboards/requirements.txt" ]; then
    echo "🔧 Corrigiendo error en requirements.txt..."
    sed -i 's/sycopg2-binary/psycopg2-binary/g' api-dashboard/dashboards/requirements.txt
    echo "✅ requirements.txt corregido"
fi

# Configurar Git
git config --global user.email "pashitox@users.noreply.github.com"
git config --global user.name "pashitox"

# Inicializar repositorio si no existe
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/pashitox/nitro-system.git
fi

# Hacer commit
git add .
git commit -m "Deploy fix: $(date '+%Y-%m-%d %H:%M:%S')" || true

# Forzar push si es necesario
git push -f origin main || echo "Push falló, continuando con build..."

# Login a Docker
echo "$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin

# Construir directamente desde el Dockerfile correcto
echo "🏗️ Construyendo imagen de Streamlit..."
docker build -t ghcr.io/pashitox/nitro-system:latest ./api-dashboard/dashboards

# Subir imagen
echo "📤 Subiendo imagen a GHCR..."
docker push ghcr.io/pashitox/nitro-system:latest

# Detener servicios previos
echo "🛑 Deteniendo servicios previos..."
docker compose -f docker-compose.prod.yml down

# Desplegar
echo "🚀 Desplegando servicios..."
docker compose -f docker-compose.prod.yml up -d

echo "✅ Despliegue completado!"
echo "📊 Streamlit: http://localhost:8501"
echo "📈 Grafana: http://localhost:3000"
echo "🐘 PostgreSQL: localhost:5432"

# Verificar que los servicios estén corriendo
echo "🔍 Verificando servicios..."
sleep 5
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"