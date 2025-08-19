#!/bin/bash

# Configurar Git
git config --global user.email "pashitox@users.noreply.github.com"
git config --global user.name "pashitox"

# Inicializar y subir el repositorio
git init
git remote add origin https://github.com/pashitox/nitro-system.git
git add .
git commit -m "Initial commit: Nitro System deployment"
git branch -M main
git push -u origin main

# Construir y subir las imágenes
export GITHUB_TOKEN="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"

# Login a GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u pashitox --password-stdin

# Construir imágenes
docker compose -f docker-compose.prod.yml build

# Taggear correctamente
docker tag streamlit ghcr.io/pashitox/nitro-system:latest

# Subir imágenes
docker push ghcr.io/pashitox/nitro-system:latest

# Desplegar
docker compose -f docker-compose.prod.yml up -d

echo "✅ Despliegue completado!"
echo "📊 Streamlit disponible en: http://localhost:8501"
echo "📈 Grafana disponible en: http://localhost:3000"