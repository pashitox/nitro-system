FROM apache/airflow:2.6.1

# Cambiar a root para instalar dependencias del sistema
USER root

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean

# Copiar requirements.txt en un lugar temporal y arreglar permisos generales
COPY requirements.txt /tmp/requirements.txt
RUN chmod 644 /tmp/requirements.txt && \
    mkdir -p /opt/airflow && chmod -R 777 /opt/airflow
    
COPY entrypoint.sh /opt/airflow/entrypoint.sh
RUN chmod +x /opt/airflow/entrypoint.sh


# Volver al usuario airflow para instalar paquetes
USER airflow
RUN pip install --no-cache-dir -r /tmp/requirements.txt
