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

tables = [
    "categories",
    "customer_customer_demo",
    "customer_demographics",
    "customers",
    "employee_territories",
    "employees",
    "orders",
    "products",
    "region",
    "shippers",
    "territories",
    "us_states"
]


with DAG(
    dag_id="indicium-northwind-elt",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
):
    
    csv_to_csv = BashOperator(
        task_id="csv_to_csv",
        bash_command=f"""cd {PROJECT_ROOT}; 
                        meltano config target-csv set output_path {folder_verify('csv')}; 
                        meltano el tap-csv target-csv"""
    )     

    postgres_to_csv = BashOperator(
        task_id="postgres_to_csv",
        bash_command=f"""
            cd {PROJECT_ROOT};
            for table in {' '.join(tables)};
            do
                mkdir -p ../data/postgres/$table/$(date +%F);
                meltano config target-csv set output_path ../data/postgres/$table/$(date +%F);
                meltano el tap-postgres target-csv --select "public-$table.*";
            done
        """
    )