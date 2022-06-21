import logging
from typing import Optional

from google.api_core import client_options
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CloudRunJob:

    def __init__(self, region: str, project_id: str, name: str):
        """
        Represents a Cloud Run Job, to be fetched, created, run or cancelled.
        :param project_id: The project in which to run the Cloud Run Job
        :param name: The Job name
        :param region: The region in which to run the Cloud Run Job
        """

        self.project_id = project_id
        self.name = name
        self.region = region

        self.__gcp_client = build('run', 'v1', client_options=client_options.ClientOptions(
            api_endpoint=f"https://{self.region}-run.googleapis.com"))

        self.job_address = f"namespaces/{self.project_id}/jobs/{self.name}"
        self.specification = self.__get()
        self.__execution_id = None

    def __get(self) -> Optional[dict]:
        """
        Get the specification of the job with the given name in the given region and project on Cloud Run.
        :return: The job spec as JSON, or None if the job does not exist.
        """
        try:
            return self.__gcp_client.namespaces().jobs().get(name=self.job_address).execute()
        except HttpError as e:
            if e.status_code == 404:
                return None
            else:
                raise

    def delete(self) -> None:
        """
        Delete the Job with the given name in the given region and project on Cloud Run.
        :return: None
        """
        if self.specification:
            self.__gcp_client.namespaces().jobs().delete(name=self.job_address).execute()
        self.specification = None

    def create(self,
               annotations: dict,
               image_address: str,
               command: str,
               args: list[str],
               environment_variables: dict,
               working_directory: str,
               port_number: int,
               max_retries: int,
               timeout_seconds: int,
               service_account_email_address: str,
               cpu_limit: int,
               memory_limit: str
               ) -> None:
        """
        Create a Cloud Run Job with the given specification in the given project. Job may then be executed with CloudRunJob.run().
        :param cpu_limit: Max number of CPUs to assign to the container.
        :param memory_limit: A fixed or floating point number followed by a unit: G or M corresponding to gigabyte or megabyte, respectively, or use the power-of-two equivalents: Gi or Mi corresponding to gibibyte or mebibyte respectively.
        :param annotations: Annotations is an unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata. More info: https://kubernetes.io/docs/user-guide/annotations. A dictionary of annotation key-value pairs, e.g. { "name": "wrench", "mass": "1.3kg", "count": "3" }
        :param image_address: URL of the Container image.
        :param command:
        :param args: Arguments to the entrypoint. The docker image's CMD is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged.
        :param environment_variables: Environment variables to set in the container, as a dictionary of name-value pairs.
        :param working_directory: Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image.
        :param port_number: TCP port to expose from the container. The specified port must be listening on all interfaces (0.0.0.0) within the container to be accessible. If omitted, a port number will be chosen and passed to the container through the PORT environment variable for the container to listen on.
        :param max_retries: Number of retries allowed per task, before marking this job failed.
        :param timeout_seconds: Duration in seconds the task may be active before the system will actively try to mark it failed and kill associated containers. This applies per attempt of a task, meaning each retry can run for the full timeout.
        :param service_account_email_address: Email address of the IAM service account associated with the task of a job execution. The service account represents the identity of the running task, and determines what permissions the task has.
        :return:
        """

        if self.specification is not None:
            logging.warning(
                "A Cloud Run Job already exists with this name in this project and region. It will be overwritten.")
            self.delete()

        # While Cloud Run jobs is in pre-release, explicitly allow use of this Launch Stage. https://cloud.google.com/run/docs/troubleshooting#launch-stage-validation
        annotations = annotations | {"run.googleapis.com/launch-stage": "BETA"}

        job_config = {
            "apiVersion": "run.googleapis.com/v1",
            "kind": "Job",
            "metadata": {
                "name": self.name,
                "annotations": annotations
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": annotations
                    },
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "image": image_address,
                                        "command": [command],
                                        "args": args,
                                        "env": [{"name": k, "value": v} for k, v in environment_variables.items()],
                                        "resources": {
                                            "limits": {
                                                "cpu": str(cpu_limit),
                                                "memory": memory_limit
                                            }
                                        },
                                        "workingDir": working_directory,
                                        "ports": [
                                            {
                                                "containerPort": port_number,
                                                "protocol": "TCP"
                                            }
                                        ],
                                    }
                                ],
                                "maxRetries": max_retries,
                                "timeoutSeconds": str(timeout_seconds),
                                "serviceAccountName": service_account_email_address
                            }
                        }
                    }
                }
            }
        }
        logging.info("Creating Cloud Run Job.")
        self.specification = self.__gcp_client.namespaces().jobs().create(parent=f"namespaces/{self.project_id}",
                                                                          body=job_config).execute()
        logging.info("✅ Created Cloud Run Job.")

    def run(self) -> None:
        """
        Run the job. Does not wait for completion - Check `self.execution` for details.
        :return: None
        """
        execution = self.__gcp_client.namespaces().jobs().run(name=self.job_address).execute()
        self.__execution_id = f"namespaces/{execution['metadata']['namespace']}/executions/{execution['metadata']['name']}"

    @property
    def execution(self) -> dict:
        """
        Get details of the most recent execution of the job.
        :return: A dictionary of execution metadata, or None if the job has not been executed since the local
        CloudRunJob object was instantiated.
        """
        return self.__gcp_client.namespaces().executions().get(name=self.__execution_id).execute() \
            if self.__execution_id \
            else None

    def cancel(self) -> None:
        """
        Cancel the job if it is currently running.
        :return: None
        """
        if self.__execution_id:
            self.__gcp_client.namespaces().executions().delete(name=self.__execution_id).execute()
