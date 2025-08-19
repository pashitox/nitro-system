from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession

def process_with_spark():
    print("===== INICIANDO PROCESO DE SPARK =====")
    spark = SparkSession.builder \
        .appName("NitroSparkProcessor") \
        .config("spark.jars.packages", 
                "org.apache.hadoop:hadoop-aws:3.3.1,"
                "org.postgresql:postgresql:42.5.0") \
        .getOrCreate()

    # Configurar acceso a MinIO
    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.endpoint", "http://minio:9000")
    hadoop_conf.set("fs.s3a.access.key", "admin")
    hadoop_conf.set("fs.s3a.secret.key", "admin12345")
    hadoop_conf.set("fs.s3a.path.style.access", "true")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    print("===== LEYENDO JSON DESDE MINIO =====")
    df = spark.read.json("s3a://raw-data/*.json")
    print(f"Registros leídos: {df.count()}")
    df.printSchema()
    df.show(5)

    df.createOrReplaceTempView("sensor_data")

    print("===== CALCULANDO PROMEDIOS =====")
    result = spark.sql("""
        SELECT sensor_id, AVG(value) as avg_value 
        FROM sensor_data 
        GROUP BY sensor_id
    """)
    result.show(5)

    print("===== GUARDANDO RESULTADOS EN POSTGRES =====")
    result.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres/nitro_db") \
        .option("dbtable", "sensor_aggregations") \
        .option("user", "nitro_user") \
        .option("password", "nitro_pass") \
        .option("driver", "org.postgresql.Driver") \
         .mode("overwrite") \
        .save()
    print("===== PROCESO COMPLETADO CON ÉXITO =====")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
}

dag = DAG(
    'nitro_data_pipeline',
    default_args=default_args,
    schedule_interval='*/3 * * * *',  # cada 3 minutos
    catchup=False
)

process_task = PythonOperator(
    task_id='process_with_spark',
    python_callable=process_with_spark,
    dag=dag
)

