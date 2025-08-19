from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data_validation.sensor_validator import validate_sensor_data

with DAG(
    dag_id="validate_sensor_data",
    start_date=datetime(2025, 8, 1),
    schedule_interval="*/3 * * * *",  # cada 3 minutos
    catchup=False,
    tags=["validation", "simple"],
) as dag:

    validate_task = PythonOperator(
        task_id="run_sensor_validation",
        python_callable=validate_sensor_data,
    )



