from tasks.folder_verify import folder_verify
from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

## PROJECT_ROOT = '/seu/diretorio/atual/do/projeto'
PROJECT_ROOT = '/home/mim/projects/code-challenge-indicium/meltano_elt'
tables = [
    "categories", "customer_customer_demo", "customer_demographics",
    "customers", "employee_territories", "employees", "orders",
    "products", "region", "shippers", "territories", "us_states"
]

with DAG(
    dag_id="indicium-northwind-elt",
    start_date=datetime(2025, 1, 21),
    schedule="@daily",
    catchup=False
) as dag:

    csv_to_csv = BashOperator(
        task_id="csv_to_csv",
        bash_command=f"""
            cd {PROJECT_ROOT};
            mkdir -p ../data/csv/{{{{ ds }}}};
            meltano config target-csv set output_path ../data/csv/{{{{ ds }}}};
            meltano config tap-csv set files '[{{"entity": "order_details", "path": "../data/order_details.csv", "keys": ["order_id"]}}]';
            meltano el tap-csv target-csv;
            meltano config tap-csv unset files;
        """
    )

    postgres_to_csv = BashOperator(
        task_id="postgres_to_csv",
        bash_command=f"""
            cd {PROJECT_ROOT};
            for table in {' '.join(tables)};
            do
                mkdir -p "../data/postgres/$table/{{{{ ds }}}}";
                meltano config target-csv set output_path "../data/postgres/$table/{{{{ ds }}}}";
                meltano el tap-postgres target-csv --select "public-$table.*";
                CSV_PATH="../data/postgres/$table/{{{{ ds }}}}/public-$table.csv";
                if [ ! -f "$CSV_PATH" ]; then
                    COLUMNS=$(meltano invoke tap-postgres --discover | \
                        jq -r '.streams[] | select(.stream == "public-$table") | .schema.properties | keys_unsorted[]' | \
                        tr '\n' ',');
                    
                    COLUMNS=${{COLUMNS%,}};
                    echo "$COLUMNS" > "$CSV_PATH";
                fi
            done
        """
    )

    csv_to_postgres = BashOperator(
        task_id="csv_to_postgres",
        bash_command=f"""
            cd {PROJECT_ROOT};
            meltano config tap-csv set files '[{{"entity": "order_details", "path": "../data/csv/{{{{ ds }}}}/order_details.csv", "keys": ["order_id"]}}]';
            meltano config target-postgres set default_target_schema public;
            meltano el tap-csv target-postgres;

            for table in {' '.join(tables)};
            do
                CSV_PATH="../data/postgres/$table/{{{{ ds }}}}/public-$table.csv"
                
                if [ ! -f "$CSV_PATH" ]; then
                    echo "Creating CSV for $table";
                    mkdir -p "../data/postgres/$table/{{{{ ds }}}}";
                    echo "id" > "$CSV_PATH";
                    echo "0" >> "$CSV_PATH";
                fi

                if [ $(wc -l < "$CSV_PATH") -eq 1 ]; then
                    echo "0" >> "$CSV_PATH";
                fi

                column_id=$(head -1 "$CSV_PATH" | cut -d ',' -f1);
                meltano config tap-csv set files '[{{"entity": "'$table'", "path": "'"$CSV_PATH"'", "keys": ["'"$column_id"'"]}}]';
                meltano el tap-csv target-postgres;
            done
            
            meltano config tap-csv unset files;
        """
    )

    [csv_to_csv, postgres_to_csv] >> csv_to_postgres