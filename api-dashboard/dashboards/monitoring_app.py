import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import time

# Configuración de la página
st.set_page_config(
    page_title="Nitro Monitoring Dashboard", 
    layout="wide",
    page_icon="💡"
)
st.title("💡 Nitro Monitoring Dashboard")

# Conexión a PostgreSQL con SQLAlchemy
@st.cache_resource
def get_db_engine():
    return create_engine(
        'postgresql+psycopg2://nitro_user:nitro_pass@postgres/nitro_db'
    )

# Consulta optimizada y manejo de datos
def get_latest_data(limit=100):
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
    chart_placeholder = st.empty()
    data_placeholder = st.empty()

    while True:
        df = get_latest_data(100)
        
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
                    title='Tendencias de Sensores',
                    template='plotly_dark',
                    labels={'valor': 'Valor', 'timestamp': 'Hora'},
                    height=500
                )
                fig.update_layout(hovermode="x unified")
                
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Tabla de últimos registros
                with data_placeholder.container():
                    st.markdown("### Últimas mediciones")
                    st.dataframe(df.tail(10), hide_index=False, height=300)
            
            except Exception as e:
                st.error(f"Error al visualizar datos: {str(e)}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
