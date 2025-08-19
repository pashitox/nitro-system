#!/bin/bash

# Configurar variables
export GITHUB_TOKEN="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"
REPO_DIR="/home/user/proyecto-nitro"

cd $REPO_DIR

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
git commit -m "Deploy $(date '+%Y-%m-%d %H:%M:%S')" || true

# Forzar push si es necesario
git push -f origin main || echo "Push falló, continuando con build..."

# Login a Docker
echo "$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin

# Construir y taggear
docker compose -f docker-compose.prod.yml build

# Obtener el nombre correcto de la imagen construida
IMAGE_ID=$(docker images -q nitro-system-streamlit)

if [ ! -z "$IMAGE_ID" ]; then
    docker tag $IMAGE_ID ghcr.io/pashitox/nitro-system:latest
    docker push ghcr.io/pashitox/nitro-system:latest
else
    echo "⚠️  No se encontró la imagen construida. Construyendo directamente..."
    docker build -t ghcr.io/pashitox/nitro-system:latest ./api-dashboard/dashboards
    docker push ghcr.io/pashitox/nitro-system:latest
fi

# Detener y desplegar
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

echo "✅ Despliegue completado!"
echo "📊 Streamlit: http://localhost:8501"
echo "📈 Grafana: http://localhost:3000"
echo "🐘 PostgreSQL: localhost:5432"