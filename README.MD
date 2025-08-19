
```markdown
# 🚀 Proyecto Nitro - Sistema de Procesamiento de Datos en Tiempo Real

## 📋 Tabla de Contenidos
1. [Características](#-características)
2. [Arquitectura del Sistema](#-arquitectura-del-sistema)
3. [Servicios y Puertos](#-servicios-y-puertos)
4. [Quick Start](#-quick-start)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Notebooks de Análisis](#-notebooks-de-análisis)
7. [Flujo de Datos](#-flujo-de-datos)
8. [Configuración](#-configuración)
9. [Mantenimiento](#-mantenimiento)
10. [Troubleshooting](#-troubleshooting)

## ✨ Características

- 📊 Ingesta de datos en tiempo real con Kafka Producer
- ⚡ Procesamiento con Spark Streaming y Python
- 🔧 Orquestación con Apache Airflow
- 💾 Almacenamiento en PostgreSQL y MinIO
- 🤖 MLOps con MLflow y SHAP
- 📈 Visualización con Streamlit y Grafana
- 📓 Notebooks para análisis y modelado

## 🏗️ Arquitectura del Sistema

```
Kafka Producer → Kafka → Spark Processor → PostgreSQL/MinIO → Dashboards
                                    ↘️ ML Models → Predictions
```

## 🌐 Servicios y Puertos

| Servicio              | URL                        | Credenciales         |
|----------------------|----------------------------|----------------------|
| Airflow              | http://localhost:8080      | admin/admin          |
| Spark Master         | http://localhost:8081      | -                    |
| Streamlit Dashboard  | http://localhost:8501      | -                    |
| Grafana              | http://localhost:3000      | admin/admin123       |
| MinIO Console        | http://localhost:9001      | admin/admin12345     |
| PostgreSQL           | localhost:5432             | nitro_user/nitro_pass|

## 🚀 Quick Start

```bash
git clone <tu-repositorio>
cd proyecto-nitro
docker-compose up -d
docker-compose ps
./start-producer.sh
```

## 📁 Estructura del Proyecto

```
proyecto-nitro/
├── airflow/
├── api-dashboard/
├── kafka-producer/
│   ├── Dockerfile
│   ├── kafka_producer.py
│   └── requirements.txt
├── minio-setup/
├── notebooks/
│   ├── EDA.ipynb
│   ├── feature_engineering.ipynb
│   ├── model_training.ipynb
│   ├── mlflow_tracking.ipynb
│   ├── SHAP_analysis.ipynb
│   ├── reports/
│   ├── models/
│   └── data/
│       └── enhanced_predictions.csv
├── postgres-setup/
├── python-processor/
├── spark-processing/
├── docker-compose.yml
├── start-producer.sh
└── README.md
```

## 📓 Notebooks de Análisis

- EDA.ipynb: Exploración de datos
- feature_engineering.ipynb: Ingeniería de características
- model_training.ipynb: Entrenamiento de modelos
- mlflow_tracking.ipynb: Seguimiento de experimentos
- SHAP_analysis.ipynb: Explicabilidad de modelos

## 🔄 Flujo de Datos

1. Kafka Producer genera datos simulados
2. Kafka publica en `sensor_topic`
3. Spark procesa en tiempo real
4. PostgreSQL y MinIO almacenan los datos
5. Notebooks analizan y modelan
6. Dashboards visualizan métricas

## ⚙️ Configuración

### Variables de Entorno

```bash
POSTGRES_USER=nitro_user
POSTGRES_PASSWORD=nitro_pass
POSTGRES_DB=nitro_db

MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=admin12345

KAFKA_BROKER_ID=1
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
```

### Kafka

- auto.create.topics.enable=true
- Topic: `sensor_topic` con 1 partición

## 🛠️ Mantenimiento

```bash
docker-compose logs
docker-compose logs kafka-producer
docker-compose down
docker-compose restart kafka-producer
docker-compose ps
docker-compose exec postgres psql -U nitro_user -d nitro_db
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

## 🐛 Troubleshooting

- Kafka no inicia → revisar logs de Kafka y Zookeeper
- Producer no conecta → esperar 30-60s y verificar salud
- PostgreSQL no responde → revisar logs
- Dashboards no cargan → esperar 2-3 min y verificar puertos

### Limpieza

```bash
docker-compose down -v
docker-compose up -d --build
```

## 📝 Licencia

MIT License - ver archivo LICENSE

## 🤝 Contribución

```bash
git checkout -b feature/AmazingFeature
git commit -m 'Add some AmazingFeature'
git push origin feature/AmazingFeature
```

Abre un Pull Request 🚀

## 📞 Soporte

- Revisa Troubleshooting
- Verifica logs
- Abre un issue

---

⭐ ¡Si te gusta este proyecto, no olvides darle una estrella!
```


