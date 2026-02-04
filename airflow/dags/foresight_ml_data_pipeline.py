import os
from datetime import datetime, timedelta

from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import (
    LocalFilesystemToGCSOperator,
)

from airflow import DAG
from src.data.pipeline.core import (
    fetch_fred_data,
    fetch_sec_data,
    merge_data,
)

# Config
GCS_BUCKET = os.getenv("GCS_BUCKET", "financial-distress-data")
OUTPUT_DIR = "data/output"

default_args = {
    "owner": "foresight-ml",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="foresight_ml_data_pipeline",
    default_args=default_args,
    description="Foresight-ML data ingestion pipeline",
    schedule="@weekly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["foresight-ml", "ingestion"],
) as dag:
    fetch_sec = PythonOperator(
        task_id="fetch_sec_data",
        python_callable=fetch_sec_data,
        op_kwargs={"output_dir": OUTPUT_DIR},
    )

    fetch_fred = PythonOperator(
        task_id="fetch_fred_data",
        python_callable=fetch_fred_data,
        op_kwargs={"output_dir": OUTPUT_DIR},
    )

    merge = PythonOperator(
        task_id="merge_data",
        python_callable=merge_data,
        op_kwargs={
            "sec_path": f"{OUTPUT_DIR}/sec_filings.json",
            "fred_path": f"{OUTPUT_DIR}/fred_indicators.csv",
            "output_dir": OUTPUT_DIR,
        },
    )

    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_to_gcs",
        src=f"{OUTPUT_DIR}/merged_data.parquet",
        dst="raw/{{ ds }}/merged_data.parquet",
        bucket=GCS_BUCKET,
    )

    [fetch_sec, fetch_fred] >> merge >> upload_to_gcs
