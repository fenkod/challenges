from datetime import datetime, timedelta, date
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from challenge.newsapi_processing import Source_Headlines

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 11, 20),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

news_challenge = Source_Headlines()

# DAG Object
dag = DAG(
    'newsapi_challenge',
    default_args=default_args,
    schedule_interval="0 8 * * *",
    catchup=False,
)

start_task = DummyOperator(task_id="start",
                           retries=3,
                           dag=dag)

get_sources_task = PythonOperator(task_id="get_sources",
                                  python_callable=news_challenge.get_sources,
                                  dag=dag)

get_headlines_task = PythonOperator(task_id="get_headlines",
                                    python_callable=news_challenge.get_headlines,
                                    dag=dag)

end_task = DummyOperator(task_id="end",
                         dag=dag)

start_task >> get_sources_task >> get_headlines_task >> end_task
