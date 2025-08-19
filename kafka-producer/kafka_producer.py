from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('producer.log')
    ]
)
logger = logging.getLogger(__name__)

def create_producer():
    """Crea un productor de Kafka con reconexión automática"""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers='kafka:9092',  # Usar nombre del servicio Docker
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(2, 0, 2),
                retries=5,
                acks='all'
            )
            logger.info("✅ Productor de Kafka creado exitosamente")
            return producer
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ No se pudo conectar a Kafka después de {max_retries} intentos: {e}")
                raise
            logger.warning(f"⚠️  Intento {attempt + 1}/{max_retries}: Error conectando a Kafka. Reintentando en {retry_delay}s...")
            time.sleep(retry_delay)

def main():
    logger.info("🚀 Iniciando Kafka Producer en modo producción")
    
    try:
        producer = create_producer()
        logger.info("📤 Comenzando envío de mensajes...")

        message_count = 0
        while True:
            try:
                data = {
                    "sensor_id": f"sensor_{random.randint(0, 4)}",
                    "value": round(random.uniform(20.0, 30.0), 2),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Enviar mensaje
                future = producer.send('sensor_topic', value=data)
                
                # Esperar confirmación
                metadata = future.get(timeout=10)
                
                message_count += 1
                logger.info(f"📤 [{message_count}] Enviado a partición {metadata.partition}, offset {metadata.offset}: {data}")
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error enviando mensaje: {e}")
                # Recrear producer si hay error de conexión
                producer.close()
                producer = create_producer()
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Producer detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
    finally:
        if 'producer' in locals():
            producer.close()
        logger.info("👋 Producer finalizado")

if __name__ == "__main__":
    main()
