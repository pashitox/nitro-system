from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

def main():
    producer = KafkaProducer(
        bootstrap_servers='localhost:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Productor conectado. Enviando mensajes...")

    try:
        while True:
            data = {
                "sensor_id": f"sensor_{random.randint(0, 4)}",
                "value": round(random.uniform(20.0, 30.0), 2),
                "timestamp": datetime.now().isoformat()
            }
            producer.send('sensor_topic', value=data)
            print(f"📤 Enviado: {data}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Producer detenido")
    finally:
        producer.close()

if __name__ == "__main__":
    main()





