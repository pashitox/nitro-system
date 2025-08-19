from kafka import KafkaConsumer
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    consumer = KafkaConsumer(
        'sensor_topic',
        bootstrap_servers='localhost:29092',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    logger.info("🔍 Consumer iniciado")

    try:
        for message in consumer:
            logger.info(f"📥 Recibido: {message.value}")
    except KeyboardInterrupt:
        logger.info("\n🛑 Consumer detenido")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()