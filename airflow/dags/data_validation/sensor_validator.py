from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import DataContextConfig, InMemoryStoreBackendDefaults
from great_expectations.core.batch import RuntimeBatchRequest
from sqlalchemy import create_engine
import pandas as pd

def validate_sensor_data():
    # Conexión a PostgreSQL
    engine = create_engine("postgresql://nitro_user:nitro_pass@postgres/nitro_db")
    df = pd.read_sql("SELECT * FROM sensor_data", engine)

    # Configuración mínima de GE
    store_backend_defaults = InMemoryStoreBackendDefaults()
    data_context_config = DataContextConfig(store_backend_defaults=store_backend_defaults)
    context = BaseDataContext(project_config=data_context_config)

    # Crear suite mínima
    suite_name = "sensor_suite"
    if suite_name not in [s.expectation_suite_name for s in context.list_expectation_suites()]:
        context.create_expectation_suite(expectation_suite_name=suite_name)

    # Batch request
    batch_request = RuntimeBatchRequest(
        datasource_name="pandas_datasource",
        data_connector_name="default_runtime_data_connector",
        data_asset_name="sensor_data",
        runtime_parameters={"batch_data": df},
        batch_identifiers={"default_identifier_name": "default_identifier"},
    )

    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name,
    )

    # Definir expectativas simples
    validator.expect_column_values_to_be_between("value", min_value=20.0, max_value=30.0)
    validator.expect_column_values_to_not_be_null("sensor_id")

    # Ejecutar validación
    results = validator.validate()

    # Solo imprimir resultado
    if results.success:
        print("✅ Validación OK")
    else:
        print("❌ Validación falló")

    return results.success


