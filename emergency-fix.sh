#!/bin/bash

# Detener todo
docker compose -f docker-compose.prod.yml down
docker system prune -f

# Corregir requirements.txt MANUALMENTE
echo "streamlit==1.28.0
pandas==2.0.3
plotly==5.15.0
sqlalchemy==2.0.20
psycopg2-binary==2.9.7" > api-dashboard/dashboards/requirements.txt

# Login a GHCR
echo "$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin

# Construir imagen
docker build -t ghcr.io/pashitox/nitro-system:latest ./api-dashboard/dashboards

# Subir imagen
docker push ghcr.io/pashitox/nitro-system:latest

# Desplegar
docker compose -f docker-compose.prod.yml up -d

echo "✅ FIX DE EMERGENCIA COMPLETADO"