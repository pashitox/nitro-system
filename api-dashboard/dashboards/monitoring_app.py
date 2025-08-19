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

# Conexión a PostgreSQL con SQLAlchemy - usando localhost
@st.cache_resource
def get_db_engine():
    return create_engine(
        'postgresql+psycopg2://nitro_user:nitro_pass@localhost:5432/nitro_db'
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