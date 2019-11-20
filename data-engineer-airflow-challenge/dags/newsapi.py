from newsapi import NewsApiClient
from pandas.io.json import json_normalize
from datetime import datetime, timedelta, date
from io import StringIO
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import os
import pandas as pd
import boto3 as boto

def get_sources():
    try:
        os.environ["NEWS_API"]
    except KeyError:
        print("Please set environment variable NEW_API")
        sys.exit(1)
    newsapi=NewsApiClient(api_key=os.environ["NEWS_API"])
    english_sources=newsapi.get_sources(language="en")
    english_sources=json_normalize(english_sources['sources'])
    return(english_sources)

def get_headlines(**context):
    sources=context['task_instance'].xcom_pull(task_ids='sources_task')
    try:
        os.environ["NEWS_API"]
    except KeyError:
        print("Please set environment variable NEWS_API")
        sys.exit(1)
    newsapi=NewsApiClient(api_key=os.environ["NEWS_API"])
    bucket="dfenko-tempus"
    s3_load=boto.resource('s3')
    for source in sources['id']:
        fetch=json_normalize(newsapi.get_top_headlines(sources=source)['articles'])
        csv_buffer=StringIO()
        fetch.to_csv(csv_buffer)
        s3_load.Object(bucket, id + "/" + str(date.today()) + "_top_headlines.csv").put(Body=csv.buffer.getvalue())
        

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 4, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG Object
dag = DAG(
    'newsapi',
    default_args=default_args,
    schedule_interval="0 8 * * *",
    catchup=False,
)

dummy_operator = DummyOperator(task_id='dummy_task', retries=3, dag=dag)

sources_operator = PythonOperator(task_id='sources_task', python_callable=get_sources, dag=dag)

headlines_operator = PythonOperator(task_id='headlines_task', python_callable=get_headlines, dag=dag)

dummy_operator >> sources_operator >> headlines_operator
