#!/bin/bash

echo "🚀 Iniciando Kafka Producer en modo producción..."

# Verificar que Kafka está funcionando
echo "🔍 Verificando conexión con Kafka..."
if ! nc -z localhost 29092 2>/dev/null; then
    echo "❌ Kafka no está disponible en localhost:29092"
    echo "💡 Asegúrate de que los servicios estén corriendo: docker compose up -d kafka"
    exit 1
fi

echo "✅ Kafka disponible. Iniciando producer..."

# Ejecutar el producer directamente en el host
cd kafka-producer
python3 kafka_producer.py
