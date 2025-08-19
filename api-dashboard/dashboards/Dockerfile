FROM python:3.10-slim

WORKDIR /app

COPY monitoring_app.py ./

RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    plotly \
    sqlalchemy \
    psycopg2-binary

EXPOSE 8501

CMD ["streamlit", "run", "monitoring_app.py", "--server.port=8501", "--server.address=0.0.0.0"]