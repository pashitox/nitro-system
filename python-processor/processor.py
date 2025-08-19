from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime
import os
import time
import logging
from minio import Minio
import io

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración para PRODUCCIÓN (localhost)
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:29092').split(',')
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'database': os.getenv('POSTGRES_DB', 'nitro_db'),
    'user': os.getenv('POSTGRES_USER', 'nitro_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'nitro_pass'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}
MINIO_CONFIG = {
    'endpoint': os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
    'access_key': os.getenv('MINIO_ACCESS_KEY', 'admin'),
    'secret_key': os.getenv('MINIO_SECRET_KEY', 'admin12345'),
    'bucket': os.getenv('MINIO_BUCKET_NAME', 'raw-data'),
    'secure': False
}

def wait_for_services():
    """Esperar a que los servicios estén disponibles"""
    logger.info("⏳ Esperando que servicios estén listos...")
    time.sleep(10)

def create_postgres_connection():
    """Crear conexión a PostgreSQL"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            logger.info("✅ Conexión PostgreSQL establecida")
            return conn
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ Error PostgreSQL después de {max_retries} intentos: {e}")
                raise
            logger.warning(f"⚠️  Intento {attempt + 1}/{max_retries}: Error PostgreSQL. Reintentando en 5s...")
            time.sleep(5)

def create_minio_client():
    """Crear cliente MinIO"""
    try:
        client = Minio(
            MINIO_CONFIG['endpoint'],
            access_key=MINIO_CONFIG['access_key'],
            secret_key=MINIO_CONFIG['secret_key'],
            secure=MINIO_CONFIG['secure']
        )
        # Verificar conexión
        client.list_buckets()
        logger.info("✅ Cliente MinIO creado")
        return client
    except Exception as e:
        logger.error(f"❌ Error MinIO: {e}")
        return None

def create_kafka_consumer():
    """Crear consumer de Kafka"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            consumer = KafkaConsumer(
                'sensor_topic',
                bootstrap_servers=KAFKA_BROKERS,
                auto_offset_reset='earliest',
                group_id='processor-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=10000
            )
            logger.info("✅ Consumer Kafka creado")
            return consumer
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ Error Kafka después de {max_retries} intentos: {e}")
                raise
            logger.warning(f"⚠️  Intento {attempt + 1}/{max_retries}: Error Kafka. Reintentando en 5s...")
            time.sleep(5)

def ensure_table_exists(conn):
    """Asegurar que la tabla existe"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    sensor_id VARCHAR(50) NOT NULL,
                    value FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            conn.commit()
        logger.info("✅ Tabla sensor_data verificada")
    except Exception as e:
        logger.error(f"❌ Error creando tabla: {e}")

def save_to_minio(client, data):
    """Guardar datos en MinIO"""
    try:
        object_name = f"sensor_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        data_bytes = json.dumps(data).encode('utf-8')
        client.put_object(
            MINIO_CONFIG['bucket'],
            object_name,
            io.BytesIO(data_bytes),
            len(data_bytes),
            content_type='application/json'
        )
        logger.info(f"💾 Guardado en MinIO: {object_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Error MinIO: {e}")
        return False

def process_message(data, conn, minio_client):
    """Procesar un mensaje"""
    try:
        # Guardar en MinIO
        if minio_client:
            save_to_minio(minio_client, data)
        
        # Insertar en PostgreSQL
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sensor_data (sensor_id, value, timestamp)
                VALUES (%s, %s, %s)
            """, (data['sensor_id'], data['value'], data['timestamp']))
            conn.commit()
        
        logger.info(f"�� Procesado: {data['sensor_id']} - {data['value']}")
        
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}")
        if conn:
            conn.rollback()

def main():
    logger.info("🚀 Iniciando Processor en modo producción")
    wait_for_services()
    
    try:
        # Inicializar conexiones
        pg_conn = create_postgres_connection()
        minio_client = create_minio_client()
        consumer = create_kafka_consumer()
        
        ensure_table_exists(pg_conn)
        
        logger.info("📡 Escuchando mensajes de Kafka...")
        
        message_count = 0
        for message in consumer:
            message_count += 1
            process_message(message.value, pg_conn, minio_client)
            
            if message_count % 10 == 0:
                logger.info(f"📊 Mensajes procesados: {message_count}")
                
    except KeyboardInterrupt:
        logger.info("🛑 Processor detenido por usuario")
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
    finally:
        if 'pg_conn' in locals():
            pg_conn.close()
        if 'consumer' in locals():
            consumer.close()
        logger.info("👋 Processor finalizado")

if __name__ == "__main__":
    main()
