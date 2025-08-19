#!/bin/bash
echo "🚀 Iniciando Kafka Producer..."

# Verificar si el directorio kafka-producer existe
if [ ! -d "kafka-producer" ]; then
    echo "❌ Directorio kafka-producer no encontrado"
    exit 1
fi

# Construir y ejecutar el producer
docker-compose up -d --build kafka-producer

echo "⏳ Esperando a que el producer se inicie..."
sleep 5

# Verificar logs del producer
echo "📋 Verificando logs del producer..."
docker-compose logs kafka-producer --tail=20

echo "✅ Producer iniciado. Para ver logs en tiempo real:"
echo "   docker-compose logs -f kafka-producer"
