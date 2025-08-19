FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para cachear
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY monitoring_app.py .

# Exponer puerto
EXPOSE 8501

# Ejecutar la aplicación
CMD ["streamlit", "run", "monitoring_app.py", "--server.port=8501", "--server.address=0.0.0.0"]