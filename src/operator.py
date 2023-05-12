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
from typing import Sequence, Optional, List

from .cloud_run import CloudRunJob, Secret, SecretType
from .data import CloudRunRegions
from airflow import AirflowException
from airflow.models import BaseOperator, Variable
from airflow.utils.context import Context
from google.auth import default

ENVIRONMENT_GCP_PROJECT: str = default()[1]


class VertFlowOperator(BaseOperator):
    def __init__(  # type: ignore
        self,
        name: str,
        image_address: str,
        service_account_email_address: str,
        command: Optional[str] = None,
        arguments: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        co2_signal_api_key: Optional[str] = None,
        working_directory: str = None,
        port_number: int = 8080,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        initialisation_timeout_seconds: int = 60,
        cpu_limit: int = 1,
        environment_variables: Optional[dict] = None,
        memory_limit: str = "512Mi",
        annotations: Optional[dict] = None,
        allowed_regions: Optional[Sequence[str]] = None,
        secrets: Optional[Sequence[Secret]] = None,
        **kwargs,
    ) -> None:
        """
        Execute a job in a Docker container on Cloud Run. Given a collection of allowed regions that the job can run in,
        deploys the job to run in the region with the lowest carbon intensity at execution time.

        :param project_id: The project in which to run the Cloud Run Job. Defaults to project set by local user or service account.
        :param name: The Job name
        :param allowed_regions: The regions in which the job is allowed to run. The greenest is picked at runtime.
        Set to None to allow any region.
        :param co2_signal_api_key: The auth token for the CO2 Signal API from which to obtain carbon intensity data. If not provided, will be read from Airflow Variable `VERTFLOW_API_KEY`.
        :param cpu_limit: Max number of CPUs to assign to the container.
        :param memory_limit: A fixed or floating point number followed by a unit: G or M corresponding to gigabyte or
        megabyte, respectively, or use the power-of-two equivalents: Gi or Mi corresponding to gibibyte or mebibyte
        respectively.
        :param annotations: Annotations is an unstructured key value map stored with a resource that may be set by
        external tools to store and retrieve arbitrary metadata. More info:
        https://kubernetes.io/docs/user-guide/annotations.
        A dictionary of annotation key-value pairs, e.g. { "name": "wrench", "mass": "1.3kg", "count": "3" }
        :param image_address: URL of the Container image.
        :param command: The command to run inside the container.
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
        :param secrets: Secrets to be passed to the container from Google Secrets Manager.
        """

        self.project_id: str = project_id or ENVIRONMENT_GCP_PROJECT
        assert (
            self.project_id is not None
        ), "You must provide a project ID, as one could not be determined from the environment."

        self.co2_signal_api_key = co2_signal_api_key or Variable.get(
            "VERTFLOW_API_KEY", None
        )
        assert (
            self.co2_signal_api_key is not None
        ), "You must provide the co2_signal_api_key argument or set the VERTFLOW_API_KEY Airflow Variable."

        self.name = name
        self.allowed_regions = allowed_regions
        self.annotations = annotations or {}
        self.image_address = image_address
        self.command = command
        self.arguments = arguments
        self.environment_variables = environment_variables or {}
        self.working_directory = working_directory
        self.port_number = port_number
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.initialisation_timeout_seconds = initialisation_timeout_seconds
        self.service_account_email_address = service_account_email_address
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.secrets = secrets

        super().__init__(resources=None, **kwargs)

    def execute(self, context: Context) -> None:
        art = """
                                                                       .-'''-.                  
                                                              .---.   '   _    \                
 .----.     .----.   __.....__                                |   | /   /` '.   \               
  \\    \\   /    /.-''         '.                         _.._ |   |.   |     \\  '       _     _ 
   '   '. /'   //     .-''"'-.  `. .-,.--.      .|     .' .._||   ||   '      |  '/\\    \\\\   // 
   |    |'    //     /________\\   \\|  .-. |   .' |_    | '    |   |\\    \\     / / `\\\\  //\\\\ //  
   |    ||    ||                  || |  | | .'     | __| |__  |   | `.   ` ..' /    \\`//  \\'/   
   '.   `'   .'\\    .-------------'| |  | |'--.  .-'|__   __| |   |    '-...-'`      \\|   |/    
    \\        /  \\    '-.____...---.| |  '-    |  |     | |    |   |                   '         
     \\      /    `.             .' | |        |  |     | |    |   |                             
      '----'       `''-...... -'   | |        |  '.'   | |    '---'                             
                                   |_|        |   /    | |                                      
                                              `'-'     |_|                                      
        """
        logging.info(art)
        logging.info("VertFlow is finding the greenest region for your Cloud Run Job.")
        cloud_run_regions = CloudRunRegions(self.project_id, self.co2_signal_api_key)

        try:
            greenest = cloud_run_regions.greenest(self.allowed_regions)
            closest = cloud_run_regions.closest

            saving = float(closest['carbon_intensity']) - float(greenest['carbon_intensity'])
            if saving > 0:
                outcome = f"{saving} gCO2eq/kWh less than"
            elif saving < 0:
                outcome = f"{saving} gCO2eq/kWh more than"
            else:
                outcome = "the same as"

            logging.info(
                f"Deploying Cloud Run Job {self.name} in {greenest['name']} ({greenest['id']}) "
                f"where carbon intensity is {greenest['carbon_intensity']} gCO2eq/kWh. "
                f"This is {outcome} your closest region {closest['name']} ({closest['id']})."
            )

            greenest_region_id = str(greenest["id"])

        except (ConnectionError, LookupError) as e:
            greenest_region_id = str(
                self.allowed_regions[0]
                if self.allowed_regions
                else cloud_run_regions.closest
            )
            logging.warning(
                f"Deploying Cloud Run Job {self.name} in region {greenest_region_id} as it was not possible to determine the greenest region:\n{repr(e)}"
            )

        self.job = CloudRunJob(
            greenest_region_id,
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
            self.secrets,
        )

        logging.debug(
            f"Created a Cloud Run job with specification:\n{self.job.specification}"
        )

        self.job.run()
        execution = self.job.execution
        logging.debug(f"Job run complete:\n{execution}")
        if not self.job.executed_successfully:
            raise AirflowException(
                f"Cloud Run job failed. View execution logs at: {self.job.execution_log_uri}"
            )

    def on_kill(self) -> None:
        self.job.cancel()
