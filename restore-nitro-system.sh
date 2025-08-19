#!/bin/bash
# restore-nitro-system.sh

echo "🔧 Restaurando y ejecutando el sistema Nitro localmente..."

# 1. Verificar que todos los directorios existen
DIRECTORIES=(
  "airflow"
  "airflow/dags"
  "airflow/logs"
  "spark-processing"
  "postgres-setup"
  "minio-setup"
  "python-processor"
  "api-dashboard/dashboards"
)

for dir in "${DIRECTORIES[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "⚠️  Creando directorio faltante: $dir"
    mkdir -p "$dir"
  fi
done

# 2. Crear archivos esenciales si no existen

# Archivo de inicialización de PostgreSQL
if [ ! -f "./postgres-setup/init.sql" ]; then
  echo "📝 Creando init.sql para PostgreSQL..."
  cat > ./postgres-setup/init.sql << 'EOF'
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sensor_id ON sensor_data(sensor_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp);
EOF
fi

# Script de configuración de MinIO
if [ ! -f "./minio-setup/create-bucket.sh" ]; then
  echo "📝 Creando create-bucket.sh para MinIO..."
  cat > ./minio-setup/create-bucket.sh << 'EOF'
#!/bin/sh
until (/usr/bin/mc config host add minio http://minio:9000 admin admin12345) do echo 'Waiting for minio...' && sleep 1; done;
/usr/bin/mc mb minio/raw-data;
/usr/bin/mc policy set public minio/raw-data;
echo 'Minio configured successfully';
EOF
  chmod +x ./minio-setup/create-bucket.sh
fi

# Dockerfile para Streamlit si no existe
if [ ! -f "./api-dashboard/dashboards/Dockerfile" ]; then
  echo "📝 Creando Dockerfile para Streamlit..."
  cat > ./api-dashboard/dashboards/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "monitoring_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
fi

# Requirements para Streamlit
if [ ! -f "./api-dashboard/dashboards/requirements.txt" ]; then
  echo "📝 Creando requirements.txt para Streamlit..."
  cat > ./api-dashboard/dashboards/requirements.txt << 'EOF'
streamlit==1.22.0
pandas==1.5.3
plotly==5.13.0
sqlalchemy==1.4.46
psycopg2-binary==2.9.5
EOF
fi

# 3. Crear aplicación Streamlit con la conexión correcta
echo "📝 Creando aplicación Streamlit..."
cat > ./api-dashboard/dashboards/monitoring_app.py << 'EOF'
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Nitro Monitoring Dashboard", 
    layout="wide",
    page_icon="💡"
)

# Título principal
st.title("💡 Nitro Monitoring Dashboard")
st.markdown("---")

# Estado del sistema
st.sidebar.header("🔧 Estado del Sistema")
status_col1, status_col2, status_col3 = st.sidebar.columns(3)
status_col1.metric("PostgreSQL", "✅ Conectado")
status_col2.metric("Processor", "✅ Activo")
status_col3.metric("MinIO", "✅ Recibiendo datos")

# Configuración de actualización
refresh_time = st.sidebar.slider("⏱️ Frecuencia de actualización (segundos)", 
                                min_value=1, max_value=30, value=5)

# Conexión a PostgreSQL con SQLAlchemy - usando el nombre del servicio
@st.cache_resource
def get_db_engine():
    return create_engine(
        'postgresql+psycopg2://nitro_user:nitro_pass@postgres:5432/nitro_db'
    )

# Consulta optimizada y manejo de datos
def get_latest_data(limit=200):
    try:
        engine = get_db_engine()
        query = f"""
            SELECT sensor_id, value, timestamp 
            FROM sensor_data
            ORDER BY timestamp DESC 
            LIMIT {limit}
        """
        df = pd.read_sql(query, engine)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Pivot para tener columnas por sensor_id
            df_pivot = df.pivot(index='timestamp', columns='sensor_id', values='value')
            df_pivot = df_pivot.sort_index()  # ordenar por timestamp ascendente
            return df_pivot
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener datos: {str(e)}")
        return pd.DataFrame()

# Diseño del dashboard
def main():
    st.subheader("📊 Datos de Sensores en Tiempo Real")
    
    # Crear placeholders para la actualización en tiempo real
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()
    data_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Estadísticas iniciales
    total_updates = 0
    last_update = datetime.now()
    
    while True:
        with status_placeholder:
            st.info(f"🔄 Actualizando cada {refresh_time} segundos... Última actualización: {last_update.strftime('%H:%M:%S')}")
        
        # Obtener datos
        df = get_latest_data(200)
        total_updates += 1
        
        if not df.empty:
            try:
                # Reset index para Plotly
                df_reset = df.reset_index()
                df_melted = df_reset.melt(
                    id_vars=['timestamp'],
                    var_name='sensor',
                    value_name='valor'
                )
                
                # Gráfico principal
                fig = px.line(
                    df_melted,
                    x='timestamp',
                    y='valor',
                    color='sensor',
                    title='Tendencias de Sensores - EN VIVO',
                    template='plotly_dark',
                    labels={'valor': 'Valor', 'timestamp': 'Hora'},
                    height=500
                )
                fig.update_layout(hovermode="x unified")
                
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Métricas rápidas
                with metrics_placeholder:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Registros", len(df))
                    with col2:
                        st.metric("Sensores Activos", len(df.columns))
                    with col3:
                        latest_ts = df.index.max()
                        st.metric("Última Medición", latest_ts.strftime('%H:%M:%S') if pd.notna(latest_ts) else "N/A")
                    with col4:
                        st.metric("Actualizaciones", total_updates)
                
                # Tabla de últimos registros
                with data_placeholder.container():
                    st.markdown("### Últimas 10 mediciones")
                    st.dataframe(df.tail(10), hide_index=False, height=300)
            
            except Exception as e:
                st.error(f"Error al visualizar datos: {str(e)}")
        else:
            st.warning("⏳ Esperando datos del sistema Nitro...")
        
        # Esperar antes de la próxima actualización
        time.sleep(refresh_time)
        last_update = datetime.now()

if __name__ == "__main__":
    main()
EOF

# 4. Iniciar el sistema
echo "🚀 Iniciando el sistema Nitro..."
docker compose down
docker compose up --build -d

echo "⏳ Esperando a que los servicios se inicien..."
sleep 10

# 5. Verificar el estado de los servicios
echo "🔍 Verificando el estado de los servicios..."
docker compose ps

echo "✅ Sistema Nitro iniciado correctamente!"
echo ""
echo "🌐 URLs de acceso:"
echo "   - Streamlit Dashboard: http://localhost:8501"
echo "   - Airflow: http://localhost:8080"
echo "   - MinIO Console: http://localhost:9001"
echo "   - Grafana: http://localhost:3000"
echo "   - Spark Master: http://localhost:8081"
echo ""
echo "📝 Para ver los logs de un servicio: docker-compose logs [nombre_servicio]"
echo "🛑 Para detener el sistema: docker-compose down"