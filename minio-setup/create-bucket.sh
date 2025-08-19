#!/bin/sh
set -e

ACCESS_KEY="admin"            
SECRET_KEY="admin12345"       

until mc alias set localminio http://minio:9000 $ACCESS_KEY $SECRET_KEY >/dev/null 2>&1; do
  sleep 1
done

echo "🛠 Creando bucket raw-data..."
mc mb --ignore-existing localminio/raw-data || echo "ℹ️ El bucket ya existe"
mc policy set public localminio/raw-data || echo "ℹ️ No se pudo establecer política"
echo "✅ Configuración de MinIO completada"

