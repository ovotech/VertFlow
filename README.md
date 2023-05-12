<dl>
  <h1>
        <div align=center><img src="https://storage.googleapis.com/vertflow/logo.png" alt="logo"/></div>
    <div align=center>VertFlow</div>
  </h1>
  <p align="center"><i>Run Docker containers on Airflow using green energy</i></p>
  <p align="center"><a href="https://drive.google.com/file/d/15XDWTu4kZfxE-SHAQcyMokr52gE_zGhv/view"><img src="https://storage.googleapis.com/vertflow/video_screenshot.png" width="358" height="201"  alt="Video Demo"/></a></p>
</dl>

## 📖 About

**VertFlow is an [Airflow](https://airflow.apache.org/) operator for
running [Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs) on Google Cloud Platform in green data
centres.**  
Cloud Run is a serverless container runtime, meaning you BYO Docker image and emit carbon only when the job is running.
This is *easier, cheaper and greener* than managing a Kubernetes cluster spinning 24/7.

**Not all data centres are created equal.**  
Data centres run on electricity generated from various sources, including fossil fuels which emit harmful carbon
emissions. Some data centres are greener than others, using electricity from renewable sources such as wind and hydro.  
When you deploy a container on Airflow using the VertFlow operator, it will run your container in the greenest GCP data
centre possible.

> ℹ️ Use VertFlow on [Cloud Composer 2](https://cloud.google.com/composer/docs/composer-2/composer-versioning-overview)
> to save even
> more money and CO2.

## 🔧 How to install

1. `pip install VertFlow` on your Airflow instance.
2. Ensure your Airflow scheduler has outbound access to the public internet and the `roles/run.developer` Cloud IAM
   role.
3. Get an [API Key for CO2 Signal](https://www.co2signal.com/), free for non-commercial use. Store in an Airflow variable called `VERTFLOW_API_KEY`.

> ℹ️ If you're using Cloud Composer, these instructions may be helpful:
> * [Installing PyPI packages](https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#install-package)
> * [Setting up internet access](https://cloud.google.com/composer/docs/concepts/private-ip#public_internet_access_for_your_workflows)
> * [About service accounts for Cloud Composer](https://cloud.google.com/composer/docs/composer-2/access-control#about-service)

## 🖱 How to use

Use the [`VertFlowOperator`](https://github.com/ovotech/VertFlow/blob/main/src/operator.py#L30) to instantiate a task in your DAG.
Provide:

* The address of the Docker image to run.
* A runtime specification, e.g. timeout and memory limits.
* A set of allowed regions to run the job in, based on your latency, data governance and other considerations. VertFlow
  picks the greenest one.

```python
from VertFlow.operator import VertFlowOperator
from airflow import DAG

with DAG(
        dag_id="hourly_dag_in_green_region",
        schedule_interval="@hourly"
) as dag:
    task = VertFlowOperator(
        image_address="us-docker.pkg.dev/cloudrun/container/job:latest",
        name="hello-world",
        allowed_regions=["europe-west1", "europe-west4"],
        command="echo",
        arguments=["Hello World"],
        service_account_email_address="my-service-account@embroidered-elephant-739.iam.gserviceaccount.com",
        ...
    )
```

## 🔌🗺 Shout out to CO2 Signal

VertFlow works thanks to real-time global carbon intensity data, gifted to the world for non-commercial use
by [CO2 Signal](https://www.co2signal.com/).

## 🤝 How to contribute

Found a bug or fancy resolving an issue? We welcome Pull Requests!
