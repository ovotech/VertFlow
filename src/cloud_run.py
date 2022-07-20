"""
Copyright 2022 OVO Energy Ltd

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from collections.abc import Callable
from time import sleep
from typing import Optional, Dict, Any

from google.api_core.client_options import ClientOptions
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def wait_until(  # type: ignore
    condition: Callable[..., bool],
    timeout_seconds: int,
    wait_interval_seconds: int = 5,
    *args,
    **kwargs,
) -> None:
    sleep(wait_interval_seconds)
    waited_for_seconds = wait_interval_seconds
    while not condition(*args, **kwargs):
        if waited_for_seconds > timeout_seconds:
            raise TimeoutError(
                f"Timeout exceeded waiting for condition: {condition.__code__}"
            )
        sleep(wait_interval_seconds)
        waited_for_seconds += wait_interval_seconds


class Specification:
    def __init__(self, spec: Optional[dict]) -> None:
        self.spec = spec

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Specification):
            return False

        if self.spec and other.spec:
            logging.debug(f"Comparing specification {self.spec} with {other.spec}...")
            are_equal = (
                (
                    str(self.spec["spec"]["template"]["spec"]["template"]["spec"])
                    == str(other.spec["spec"]["template"]["spec"]["template"]["spec"])
                )
                and (
                    str(self.spec["metadata"]["name"])
                    == str(other.spec["metadata"]["name"])
                )
                and (
                    str(self.spec["spec"]["template"]["metadata"]["annotations"])
                    == str(other.spec["spec"]["template"]["metadata"]["annotations"])
                )
            )
            logging.debug(f"Specifications equal: {are_equal}")

            return are_equal
        else:
            return (self.spec is None) == (other.spec is None)


class CloudRunJob:
    def __init__(self, region: str, project_id: str, name: str) -> None:
        """
        Represents a Cloud Run Job, to be fetched, created, run or cancelled.
        :param project_id: The project in which to run the Cloud Run Job
        :param name: The Job name
        :param region: The region in which to run the Cloud Run Job
        """

        self.__execution_id: Optional[str] = None
        self.project_id = project_id
        self.name = name
        self.region = region

        self.__gcp_client = build(
            "run",
            "v1",
            client_options=ClientOptions(
                api_endpoint=f"https://{self.region}-run.googleapis.com"
            ),
        )

        self.job_address = f"namespaces/{self.project_id}/jobs/{self.name}"

    @property
    def specification(self) -> Optional[Dict[str, Any]]:
        """
        Get the specification of the job with the given name in the given region and project on Cloud Run.
        :return: The job spec as JSON, or None if the job does not exist.
        """
        try:
            result: Dict[str, Any] = (
                self.__gcp_client.namespaces()
                .jobs()
                .get(name=self.job_address)
                .execute()
            )
            return result
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
            self.__gcp_client.namespaces().jobs().delete(
                name=self.job_address
            ).execute()
        wait_until(lambda: self.specification is None, 60)

    def create(
        self,
        annotations: dict,
        image_address: str,
        command: str,
        args: list[str],
        environment_variables: dict,
        working_directory: str,
        port_number: int,
        max_retries: int,
        timeout_seconds: int,
        initialisation_timeout_seconds: int,
        service_account_email_address: str,
        cpu_limit: int,
        memory_limit: str,
    ) -> None:
        """
        Create a Cloud Run Job with the given specification in the given project. Job may then be executed with
        CloudRunJob.run().

        :param cpu_limit: Max number of CPUs to assign to the container.
        :param memory_limit: A fixed or floating point number followed by a unit: G or M corresponding to gigabyte or
        megabyte, respectively, or use the power-of-two equivalents: Gi or Mi corresponding to gibibyte or mebibyte
        respectively.
        :param annotations: Annotations is an unstructured key value map stored with a resource that may be set by
        external tools to store and retrieve arbitrary metadata.
        More info: https://kubernetes.io/docs/user-guide/annotations.
        A dictionary of annotation key-value pairs, e.g. { "name": "wrench", "mass": "1.3kg", "count": "3" }
        :param image_address: URL of the Container image.
        :param command:
        :param args: Arguments to the entrypoint. The docker image's CMD is used if this is not provided. Variable
        references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the
        reference in the input string will be unchanged.
        :param environment_variables: Environment variables to set in the container, as a dictionary of name-value
        pairs.
        :param working_directory: Container's working directory. If not specified, the container runtime's default will
        be used, which might be configured in the container image.
        :param port_number: TCP port to expose from the container. The specified port must be listening on all
        interfaces (0.0.0.0) within the container to be accessible. If omitted, a port number will be chosen and passed
        to the container through the PORT environment variable for the container to listen on.
        :param max_retries: Number of retries allowed per task, before marking this job failed.
        :param timeout_seconds: Duration in seconds the task may be active before the system will actively try to mark
        it failed and kill associated containers. This applies per attempt of a task, meaning each retry can run for
        the full timeout.
        :param initialisation_timeout_seconds: Duration in seconds to wait for the job to be in a Ready state on Cloud
        Run. https://cloud.google.com/run/docs/reference/rest/v1/Condition
        :param service_account_email_address: Email address of the IAM service account associated with the task of a
        job execution. The service account represents the identity of the running task, and determines what permissions
        the task has.
        :return:
        """

        self.__run_timeout_seconds = timeout_seconds
        self.__max_retries = max_retries

        # While Cloud Run jobs is in pre-release, explicitly allow use of this Launch Stage.
        # https://cloud.google.com/run/docs/troubleshooting#launch-stage-validation
        annotations = annotations | {
            "run.googleapis.com/launch-stage": "BETA",
            "run.googleapis.com/execution-environment": "gen2",
        }

        new_specification = {
            "apiVersion": "run.googleapis.com/v1",
            "kind": "Job",
            "metadata": {"name": self.name, "annotations": annotations},
            "spec": {
                "template": {
                    "metadata": {"annotations": annotations},
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "image": image_address,
                                        "command": [command],
                                        "args": args,
                                        "env": [
                                            {"name": k, "value": v}
                                            for k, v in environment_variables.items()
                                        ],
                                        "resources": {
                                            "limits": {
                                                "cpu": str(cpu_limit),
                                                "memory": memory_limit,
                                            }
                                        },
                                        "workingDir": working_directory,
                                        "ports": [{"containerPort": port_number}],
                                    }
                                ],
                                "maxRetries": max_retries,
                                "timeoutSeconds": str(timeout_seconds),
                                "serviceAccountName": service_account_email_address,
                            }
                        }
                    },
                }
            },
        }

        if Specification(self.specification) == Specification(new_specification):
            logging.warning(
                "A Cloud Run Job already exists with an identical specification. No action taken."
            )

        else:
            if self.specification:
                logging.warning(
                    "A Cloud Run Job already exists with this name in this project and region. "
                    "It will be overwritten with the new specification provided."
                )
                self.delete()

            self.__gcp_client.namespaces().jobs().create(
                parent=f"namespaces/{self.project_id}", body=new_specification
            ).execute()

            def is_build_complete() -> bool:
                return (
                    str(self.specification["status"]["conditions"][0]["status"])
                    == "True"
                    if self.specification
                    else False
                )

            wait_until(is_build_complete, initialisation_timeout_seconds)

    def run(self, wait: bool = True) -> None:
        """
        Run the job and wait for completion.
        :param: wait: Whether to wait (i.e. block) until the job has completed on Cloud Run.
        :return: None
        """
        execution = (
            self.__gcp_client.namespaces().jobs().run(name=self.job_address).execute()
        )
        self.__execution_id = (
            f"namespaces/{execution['metadata']['namespace']}"
            f"/executions/{execution['metadata']['name']}"
        )

        logging.info(
            f"https://console.cloud.google.com/run/jobs/executions/details/{self.region}/{self.__execution_id}"
            f"/tasks?project={self.project_id}"
        )
        if wait:
            wait_until(
                lambda: self.__execution_completed() in ("True", "False"),
                self.__run_timeout_seconds * (self.__max_retries + 1),
            )

    @property
    def execution(self) -> Optional[dict]:
        """
        Get details of the most recent execution of the job.
        :return: A dictionary of execution metadata, or None if the job has not been executed since the local
        CloudRunJob object was instantiated.
        """
        return (
            self.__gcp_client.namespaces()
            .executions()
            .get(name=self.__execution_id)
            .execute()
            if self.__execution_id
            else None
        )

    @property
    def execution_log_uri(self) -> Optional[str]:
        """
        The link to the Cloud Logging page for the Cloud Run Job that has finished executing.
        """
        return self.execution["status"]["logUri"] if self.execution else None

    def __execution_completed(self) -> Optional[str]:
        return (
            next(
                condition
                for condition in self.execution["status"]["conditions"]
                if condition["type"] == "Completed"
            )["status"]
            if self.execution
            else None
        )

    @property
    def executed_successfully(self) -> bool:
        """
        Returns True if the job finished running successfully.
        """
        return self.__execution_completed() == "True"

    def cancel(self) -> None:
        """
        Cancel the job if it is currently running.
        :return: None
        """
        if self.__execution_id:
            self.__gcp_client.namespaces().executions().delete(
                name=self.__execution_id
            ).execute()
            self.__execution_id = None
        else:
            logging.warning("No job execution to cancel.")
