-- Tabla para datos crudos
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla para agregaciones
CREATE TABLE IF NOT EXISTS sensor_aggregations (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    avg_value FLOAT NOT NULL,
    calculation_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sensor_id)  -- Para evitar duplicados
);

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_sensor_id ON sensor_data(sensor_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp);