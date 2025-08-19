import json
from kafka import KafkaConsumer
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime
import os
import time
import logging
from minio import Minio
from minio.error import S3Error
import io

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka:9092').split(',')
TOPIC = os.getenv('TOPIC', 'sensor_topic')
GROUP_ID = os.getenv('GROUP_ID', 'python-processor-group')

# Configuración de PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'database': os.getenv('POSTGRES_DB', 'nitro_db'),
    'user': os.getenv('POSTGRES_USER', 'nitro_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'nitro_pass')
}

# Configuración de MinIO
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'admin12345')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'raw-data')

def create_postgres_connection(max_retries=5, delay=5):
    """Crea una conexión a PostgreSQL con reintentos"""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            logger.info("Conexión a PostgreSQL establecida")
            return conn
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Intento {attempt + 1} de {max_retries}: No se pudo conectar a PostgreSQL. Reintentando en {delay} segundos...")
            time.sleep(delay)

def ensure_table_exists(conn):
    """Asegura que la tabla exista con los índices adecuados"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(50) NOT NULL,
                value FLOAT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_sensor_id ON sensor_data(sensor_id);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp);
        """)
        conn.commit()
    logger.info("Tabla sensor_data verificada/creada")

def convert_timestamp(timestamp):
    """Convierte el timestamp a formato datetime"""
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp)
            except ValueError:
                return datetime.fromtimestamp(float(timestamp))
        return timestamp
    except Exception as e:
        logger.error(f"Error convirtiendo timestamp {timestamp}: {e}")
        raise ValueError(f"Formato de timestamp no válido: {timestamp}")

def create_minio_client():
    """Crea y retorna un cliente de MinIO"""
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def save_to_minio(client, data):
    """Guarda datos en bruto en MinIO como archivo JSON"""
    try:
        object_name = f"sensor_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        data_str = json.dumps(data)
        data_bytes = data_str.encode('utf-8')
        data_stream = io.BytesIO(data_bytes)

        client.put_object(
            MINIO_BUCKET_NAME,
            object_name,
            data_stream,
            length=len(data_bytes),
            content_type='application/json'
        )
        return True
    except S3Error as e:
        logger.error(f"Error guardando en MinIO: {e}")
        return False

def process_message(msg, conn, minio_client):
    """Procesa un mensaje de Kafka, guarda en MinIO y luego en PostgreSQL"""
    try:
        # Decodificar el mensaje
        data = msg.value if isinstance(msg.value, dict) else json.loads(msg.value)

        # 1. Guardar en MinIO (datos brutos)
        if not save_to_minio(minio_client, data):
            raise Exception("Error al guardar en MinIO")

        # 2. Validación de datos
        required_fields = ['sensor_id', 'value', 'timestamp']
        if not all(field in data for field in required_fields):
            raise ValueError(f"Faltan campos requeridos en el mensaje: {data}")

        # 3. Convertir timestamp
        timestamp = convert_timestamp(data['timestamp'])

        # 4. Insertar en PostgreSQL
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sensor_data (sensor_id, value, timestamp)
                VALUES (%s, %s, %s)
            """, (
                str(data['sensor_id']),
                float(data['value']),
                timestamp
            ))
            conn.commit()

        logger.info(f"Dato insertado: {data['sensor_id']}, {data['value']}, {timestamp}")

    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}\nMensaje: {msg.value if hasattr(msg, 'value') else msg}")
        conn.rollback()

def create_kafka_consumer():
    """Crea un consumidor de Kafka con configuración robusta"""
    for attempt in range(5):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                auto_offset_reset='earliest',
                group_id=GROUP_ID,
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Consumer de Kafka creado exitosamente")
            return consumer
        except Exception as e:
            if attempt == 4:
                raise
            logger.warning(f"Intento {attempt + 1} de 5: Error creando consumer. Reintentando...")
            time.sleep(5)

def main():
    logger.info("Iniciando procesador de datos...")

    # Esperar inicialización de servicios
    time.sleep(15)

    # Configurar conexiones
    pg_conn = create_postgres_connection()
    ensure_table_exists(pg_conn)
    consumer = create_kafka_consumer()
    minio_client = create_minio_client()

    logger.info("Listo para procesar mensajes...")

    try:
        for msg in consumer:
            process_message(msg, pg_conn, minio_client)
    except KeyboardInterrupt:
        logger.info("\n🛑 Consumer detenido")
    finally:
        consumer.close()
        pg_conn.close()
        logger.info("Conexiones cerradas")

if __name__ == "__main__":
    main()