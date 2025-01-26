from tasks.folder_verify import folder_verify

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import os

PROJECT_ROOT = '/home/mim/projects/code-challenge-indicium/meltano_elt'
MELTANO_BIN = ".meltano/run/bin"

DEFAULT_ARGS = {
    "owner": "Yasmim Abrahao",
    "depends_on_past": False,
    "catchup": False
}

with DAG(
    dag_id="indicium-northwind-elt",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
):
    path = folder_verify('csv')
    
    csv_to_csv = BashOperator(
        task_id="csv_to_csv",
        bash_command=f"cd {PROJECT_ROOT}; meltano config target-csv set output_path {path}; meltano el tap-csv target-csv"
    )