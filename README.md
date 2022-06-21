<dl>
  <h1>
    <div align=center><img src="logo.png" alt="logo"/></div>
    <div align=center>VertFlow</div>
  </h1>
  <p align="center"><i>Run Docker containers on Airflow using green energy</i></p>
</dl>

## About

**VertFlow is an [Airflow](https://airflow.apache.org/) operator for
running [Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs) on Google Cloud Platform in green data
centres.**  
Cloud Run is a serverless container runtime, meaning you BYO Docker image and emit carbon only when the job is running.
This is *easier, cheaper and greener* than managing a Kubernetes cluster spinning 24/7.

**Not all data centres are created equal.**  
Data centres run on electricity generated from various sources, including fossil fuels which lead to harmful CO2
emissions. Some data centres are greener than others, using electricity from renewable sources such as wind and hydro.  
When you deploy a container on Airflow using the VertFlow operator, it will run your container in the greenest GCP data
centre possible.

> ℹ️ Use in tandem
> with [Cloud Composer 2](https://cloud.google.com/composer/docs/composer-2/composer-versioning-overview) to save even
> more money and CO2.

## How to use

Use the `VertFlowOperator` to instantiate a task in your DAG.
Provide:

1. The address of the Docker image to run.
2. A runtime specification, e.g. timeout and memory limits.
3. A set of allowed regions to run the job in, based on latency, data governance and other considerations. VertFlow picks
  the greenest one.

```python
from airflow import DAG
from VertFlow import VertFlowOperator

with DAG(
        dag_id="hourly_dag_in_green_region",
        schedule_interval="@hourly"
) as dag:
    VertFlowOperator(
        image_address="us-docker.pkg.dev/cloudrun/container/job:latest",
        project_id="embroidered-elephant-739",
        name="hello-world",
        allowed_regions=["europe-west1", "europe-west4"],
        annotations={"key": "value"},
        command="echo",
        args=["$WORDS"],
        environment_variables={"WORDS": "Hello World"},
        working_directory="/",
        port_number="8080",
        max_retries=3,
        timeout_seconds="60s",
        service_account_email_address="my-service-account@embroidered-elephant-739.iam.gserviceaccount.com",
        cpu_limit=1,
        memory_limit="512Mi"
    )
```

## Limitations

* There is no test coverage on this library as yet. Tests will follow.
* Cloud Run Jobs is not yet Generally Available. Production use is not advised. It also has a series of limitations, e.g. tasks can run for no longer than 1 hour.
* The container running the Cloud Run Job cannot access resources on a VPC. Dynamic creation of a Serverless VPC Connector would be required, which is not supported.
* VertFlow assumes no emissions from transmitting data between regions. These may infact be non-trivial if storage and
  compute are far from each other. Charges may also be incurred in this scenario.
* VertFlow uses the [duck curve](https://en.wikipedia.org/wiki/Duck_curve) of the [UK](https://carbonintensity.org.uk/)
  to add daily shape to [Google's CFE% figures per region](https://cloud.google.com/sustainability/region-carbon#data).
  This is a placeholder pending robust real-time data.
