import datetime as dt

from VertFlow.operator import VertFlowOperator
from airflow import DAG


with DAG(
        dag_id="vertflow_test"
) as dag:
    task = VertFlowOperator(
        image_address="us-docker.pkg.dev/cloudrun/container/job:latest",
        project_id="trading-nonprod",
        name="hello-world",
        allowed_regions=["europe-west1", "europe-west4"],
        annotations={"key": "value"},
        command="sleep",
        arguments=["30"],
        environment_variables={"WORDS": "Hello World"},
        working_directory="/",
        port_number=8080,
        max_retries=3,
        timeout_seconds=60,
        initialisation_timeout_seconds=60,
        service_account_email_address="714098496902-compute@developer.gserviceaccount.com",
        cpu_limit=1,
        memory_limit="512Mi",
        start_date=dt.datetime(2022, 6, 20),
        task_id="test_vertflow_task"
    )
