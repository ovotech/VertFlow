import datetime as dt

from VertFlow.operator import VertFlowOperator
from airflow import DAG

with DAG(
        dag_id="vertflow_test"
) as dag:
    task = VertFlowOperator(
        image_address="us-docker.pkg.dev/cloudrun/container/job:latest",
        project_id="trading-nonprod",
        name="hello-world-fail",
        allowed_regions=["europe-west1", "europe-west4"],
        command="echo",
        arguments=["Hello World"],
        service_account_email_address="714098496902-compute@developer.gserviceaccount.com",
        start_date=dt.datetime(2022, 7, 1),
        task_id="test_vertflow_task"
    )
