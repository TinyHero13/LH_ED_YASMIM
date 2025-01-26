from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

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
    csv_to_csv = BashOperator(
        task_id="csv_to_csv",
        bash_command=f"cd {PROJECT_ROOT}; meltano el tap-csv target-csv"
    )