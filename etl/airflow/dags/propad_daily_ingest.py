from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

DEFAULT_ARGS = {"owner": "propad", "retries": 1}

def load_bapenda_sources(**ctx):
    print("Load internal sources… (stub)")

def load_external_sources(**ctx):
    print("Load external sources… (stub)")

def run_dbt(**ctx):
    print("Run dbt models… (stub)")

def dq_tests(**ctx):
    print("Run data quality tests… (stub)")

with DAG(
    dag_id="propad_daily_ingest",
    start_date=datetime(2025, 8, 1),
    schedule="0 2 * * *",
    default_args=DEFAULT_ARGS,
    catchup=False,
) as dag:
    t1 = PythonOperator(task_id="ingest_internal", python_callable=load_bapenda_sources)
    t2 = PythonOperator(task_id="ingest_external", python_callable=load_external_sources)
    t3 = PythonOperator(task_id="dbt_transform", python_callable=run_dbt)
    t4 = PythonOperator(task_id="dq_tests", python_callable=dq_tests)
    t1 >> t2 >> t3 >> t4
