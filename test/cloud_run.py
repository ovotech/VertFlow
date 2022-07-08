from time import time, sleep
from typing import Optional
from unittest import TestCase

from src.cloud_run import CloudRunJob, wait_until
from src.utils import intersection_equal


def create_quick_test_job(job: CloudRunJob, command: str, args: list[str]) -> None:
    job.create(
        annotations={},
        image_address="us-docker.pkg.dev/cloudrun/container/job:latest",
        command=command,
        args=args,
        environment_variables={},
        working_directory="/",
        port_number=8080,
        max_retries=0,
        timeout_seconds=30,
        initialisation_timeout_seconds=120,
        service_account_email_address="empty-no-permissions@trading-nonprod.iam.gserviceaccount.com",
        cpu_limit=1,
        memory_limit="512Mi",
    )


class TestWaitUntil(TestCase):
    def setUp(self) -> None:
        self.number_of_calls_until_returns_true = 3
        self.call_count = 0
        self.wait_interval_seconds = 5

    def condition_to_wait_for(self) -> bool:
        if self.call_count < self.number_of_calls_until_returns_true:
            self.call_count += 1
            return False
        else:
            return True

    def test_wait_until_blocks_until_condition_returns_true(self) -> None:

        time_before_wait = time()

        # Condition will return true after 15 seconds.
        wait_until(self.condition_to_wait_for, 20, self.wait_interval_seconds)

        # Validate that wait_until exits cleanly after c. 15 seconds.
        self.assertTrue(
            self.number_of_calls_until_returns_true * self.wait_interval_seconds
            < time() - time_before_wait
            <= self.number_of_calls_until_returns_true * self.wait_interval_seconds + 1
        )

    def test_wait_throws_if_timeout_is_reached_before_condition_returns_true(
        self,
    ) -> None:

        time_before_wait = time()
        timeout_seconds = 5
        exception_thrown: Optional[Exception] = None

        try:
            wait_until(
                self.condition_to_wait_for, timeout_seconds, self.wait_interval_seconds
            )
        except Exception as e:
            exception_thrown = e

        time_after_wait = time()

        # Validate that wait_until exits after timeout
        self.assertTrue(
            timeout_seconds < time_after_wait - time_before_wait <= timeout_seconds + 1
        )

        # Validate that wait_until throws a TimeoutError
        self.assertIsInstance(exception_thrown, TimeoutError)


class TestCloudRunJobEndToEnd(TestCase):
    def setUp(self) -> None:
        # Instantiate a brand new Cloud Run job.
        self.job = CloudRunJob(
            "europe-west2", "trading-nonprod", f"vertflow-e2e-test-{int(time())}"
        )

    def tearDown(self) -> None:
        self.job.delete()

    def test_end_to_end(self) -> None:
        """
        Conduct an end-to-end test of spinning up a Cloud Run Job, creating a series of executions, and deleting it.
        """

        # Validate that the job has an empty spec, as it does not exist yet.
        self.assertIsNone(self.job.specification)

        # Create a new Job with a spec prescribed locally.
        create_quick_test_job(self.job, "echo", ["Hello World"])

        # Validate that the spec is non-empty, i.e. the job was created successfully.
        spec_from_first_creation = self.job.specification
        self.assertIsNotNone(self.job.specification)

        with self.assertLogs() as captured_logs:
            # Create a new Job with an identical specification.
            create_quick_test_job(self.job, "echo", ["Hello World"])

            # Validate that no change is made.
            expected_log_message = "A Cloud Run Job already exists with an identical specification. No action taken."
        self.assertEqual(len(captured_logs.records), 1)
        self.assertEqual(captured_logs.records[0].getMessage(), expected_log_message)

        # Validate that spec from the second run is identical to the first.
        self.assertTrue(
            intersection_equal(spec_from_first_creation, self.job.specification)
        )

        # Create a new Job that is different to the first.
        create_quick_test_job(self.job, "echo", ["Hello World 2"])

        # Validate that the spec is different, i.e. the change was successfully applied.
        self.assertFalse(
            intersection_equal(spec_from_first_creation, self.job.specification)
        )

        with self.assertLogs() as captured_logs:
            # Attempt to cancel the job execution.
            self.job.cancel()

            # Validate that warning that there is nothing to cancel is presented.
            expected_log_message = "No job execution to cancel."
            self.assertEqual(len(captured_logs.records), 1)
            self.assertEqual(
                captured_logs.records[0].getMessage(), expected_log_message
            )

        # Validate that details relating to execution are empty.
        self.assertIsNone(self.job.execution)
        self.assertIsNone(self.job.execution_log_uri)
        self.assertFalse(self.job.executed_successfully)

        # Run the job
        time_before_run = time()
        self.job.run()
        execution_duration = time() - time_before_run

        # Validate that the client waited for the job to complete.
        self.assertTrue(execution_duration > 10)

        # Validate that details relating to execution are nonempty.
        self.assertIsNotNone(self.job.execution)
        self.assertIsNotNone(self.job.execution_log_uri)
        self.assertTrue(self.job.executed_successfully)

        # Run the job again, then cancel it.
        self.job.run()
        sleep(10)
        self.job.cancel()

        # Validate that details relating to execution are empty.
        self.assertIsNone(self.job.execution)
        self.assertIsNone(self.job.execution_log_uri)
        self.assertFalse(self.job.executed_successfully)

        # Create and run a new job with a spec that will fail when executed.
        create_quick_test_job(self.job, "exit", ["1"])
        self.job.run()

        # Validate that the run was not successful.
        self.assertFalse(self.job.executed_successfully)

        # Delete the job
        self.job.delete()

        # Validate that the spec is empty, i.e. the job was deleted.
        self.assertIsNone(self.job.specification)
