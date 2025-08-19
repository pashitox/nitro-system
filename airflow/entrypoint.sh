#!/bin/bash
set -e

# Esperar a que Postgres esté listo
until PGPASSWORD=nitro_pass psql -h postgres -U nitro_user -d nitro_db -c 'SELECT 1' >/dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Inicializar la base de datos solo si no está ya inicializada
if ! airflow db check-migrations >/dev/null 2>&1; then
  echo "Initializing Airflow DB..."
  airflow db init
else
  echo "Airflow DB already initialized."
fi

# Crear usuario admin solo si no existe
if ! airflow users list | grep -q "airflow"; then
  echo "Creating Airflow admin user..."
  airflow users create \
    --username airflow \
    --firstname Air \
    --lastname Flow \
    --role Admin \
    --email airflow@example.com \
    --password airflow
else
  echo "Airflow admin user already exists."
fi

# Asegurar carpeta de logs
mkdir -p /opt/airflow/logs

# Lanzar webserver y scheduler
airflow webserver &
airflow scheduler
