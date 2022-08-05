###Install VertFlow on the Cloud Composer image, to ensure no dependency conflicts or other installation failures.###

FROM europe-west2-docker.pkg.dev/cloud-airflow-releaser/airflow-worker-scheduler-2-2-5/airflow-worker-scheduler-2-2-5:cloud_composer_service_2022-07-17-RC0

ARG VERTFLOW_VERSION

USER root

# Copy installation artifacts.
COPY requirements.txt .
COPY installer.sh .

# Install pypi dependencies
RUN sh installer.sh
