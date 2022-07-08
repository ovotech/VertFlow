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
from datetime import datetime
from typing import Sequence, Optional

from VertFlow.cloud_run import CloudRunJob
from VertFlow.data import CarbonIntensityData
from airflow import AirflowException
from airflow.models import BaseOperator
from airflow.utils.context import Context


class VertFlowOperator(BaseOperator):
    def __init__(  # type: ignore
        self,
        project_id: str,
        name: str,
        image_address: str,
        command: str,
        arguments: list[str],
        service_account_email_address: str,
        working_directory: str = "/",
        port_number: int = 8080,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        initialisation_timeout_seconds: int = 60,
        cpu_limit: int = 1,
        environment_variables: dict = {},
        memory_limit: str = "512Mi",
        annotations: dict = {},
        allowed_regions: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> None:
        """
        Execute a job in a Docker container on Cloud Run. Given a collection of allowed regions that the job can run in,
        deploys the job to run in the region with the lowest carbon intensity at execution time.

        :param project_id: The project in which to run the Cloud Run Job
        :param name: The Job name
        :param allowed_regions: The regions in which the job is allowed to run. The greenest is picked at runtime.
        Set to None to allow any region.
        :param cpu_limit: Max number of CPUs to assign to the container.
        :param memory_limit: A fixed or floating point number followed by a unit: G or M corresponding to gigabyte or
        megabyte, respectively, or use the power-of-two equivalents: Gi or Mi corresponding to gibibyte or mebibyte
        respectively.
        :param annotations: Annotations is an unstructured key value map stored with a resource that may be set by
        external tools to store and retrieve arbitrary metadata. More info:
        https://kubernetes.io/docs/user-guide/annotations.
        A dictionary of annotation key-value pairs, e.g. { "name": "wrench", "mass": "1.3kg", "count": "3" }
        :param image_address: URL of the Container image.
        :param command:
        :param arguments: Arguments to the entrypoint. The docker image's CMD is used if this is not provided. Variable
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
        """

        self.project_id = project_id
        self.name = name
        self.allowed_regions = allowed_regions
        self.annotations = annotations
        self.image_address = image_address
        self.command = command
        self.arguments = arguments
        self.environment_variables = environment_variables
        self.working_directory = working_directory
        self.port_number = port_number
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.initialisation_timeout_seconds = initialisation_timeout_seconds
        self.service_account_email_address = service_account_email_address
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit

        super().__init__(resources=None, **kwargs)

    def execute(self, context: Context) -> None:
        self.job = CloudRunJob(
            CarbonIntensityData().greenest_region(
                self.allowed_regions, datetime.utcnow().time()
            ),
            self.project_id,
            self.name,
        )
        self.job.create(
            self.annotations,
            self.image_address,
            self.command,
            self.arguments,
            self.environment_variables,
            self.working_directory,
            self.port_number,
            self.max_retries,
            self.timeout_seconds,
            self.initialisation_timeout_seconds,
            self.service_account_email_address,
            self.cpu_limit,
            self.memory_limit,
        )

        logging.info(
            f"Created a Cloud Run job with specification:\n{self.job.specification}"
        )

        self.job.run()
        execution = self.job.execution
        logging.info(f"Job run complete:\n{execution}")
        if not self.job.run_completed_successfully:
            raise AirflowException(
                f"Cloud Run job failed. View execution logs at: {self.job.execution_log_uri}"
            )

    def on_kill(self) -> None:
        self.job.cancel()
