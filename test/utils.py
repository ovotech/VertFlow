from time import time
from typing import Optional
from unittest import TestCase

from src.utils import intersection_equal, wait_until


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


class TestIntersectionEqual(TestCase):
    def setUp(self) -> None:
        self.spec_1_sent = {
            "apiVersion": "run.googleapis.com/v1",
            "kind": "Job",
            "metadata": {
                "name": "vertflow-e2e-test-1657479711",
                "annotations": {
                    "run.googleapis.com/launch-stage": "BETA",
                    "run.googleapis.com/execution-environment": "gen2",
                },
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "run.googleapis.com/launch-stage": "BETA",
                            "run.googleapis.com/execution-environment": "gen2",
                        }
                    },
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "image": "us-docker.pkg.dev/cloudrun/container/job:latest",
                                        "command": ["echo"],
                                        "args": ["Hello World"],
                                        "env": [],
                                        "resources": {
                                            "limits": {"cpu": "1", "memory": "512Mi"}
                                        },
                                        "workingDir": "/",
                                        "ports": [{"containerPort": 8080}],
                                    }
                                ],
                                "maxRetries": 0,
                                "timeoutSeconds": "30",
                                "serviceAccountName": "empty-no-permissions@trading-nonprod.iam.gserviceaccount.com",
                            }
                        }
                    },
                }
            },
        }
        self.spec_1_received = {
            "apiVersion": "run.googleapis.com/v1",
            "kind": "Job",
            "metadata": {
                "name": "vertflow-e2e-test-1657479711",
                "namespace": "714098496902",
                "selfLink": "/apis/run.googleapis.com/v1/namespaces/714098496902/jobs/vertflow-e2e-test-1657479711",
                "uid": "eb00160c-13dc-4c70-a5dc-850abdec5a1b",
                "resourceVersion": "AAXjeBMXSfE",
                "generation": 1,
                "creationTimestamp": "2022-07-10T19:02:18.734980Z",
                "labels": {"cloud.googleapis.com/location": "europe-west2"},
                "annotations": {
                    "run.googleapis.com/lastModifier": "jack.lockyer-stevens@ovo.com",
                    "run.googleapis.com/creator": "jack.lockyer-stevens@ovo.com",
                    "run.googleapis.com/execution-environment": "gen2",
                    "run.googleapis.com/launch-stage": "BETA",
                },
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "run.googleapis.com/launch-stage": "BETA",
                            "run.googleapis.com/execution-environment": "gen2",
                        }
                    },
                    "spec": {
                        "taskCount": 1,
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "image": "us-docker.pkg.dev/cloudrun/container/job:latest",
                                        "command": ["echo"],
                                        "args": ["Hello World"],
                                        "workingDir": "/",
                                        "ports": [{"containerPort": 8080}],
                                        "resources": {
                                            "limits": {"cpu": "1", "memory": "512Mi"}
                                        },
                                    }
                                ],
                                "maxRetries": 0,
                                "timeoutSeconds": "30",
                                "serviceAccountName": "empty-no-permissions@trading-nonprod.iam.gserviceaccount.com",
                            }
                        },
                    },
                }
            },
            "status": {
                "observedGeneration": 1,
                "conditions": [
                    {
                        "type": "Ready",
                        "status": "True",
                        "lastTransitionTime": "2022-07-10T19:02:19.427313Z",
                    }
                ],
            },
        }

        self.spec_2_sent = {
            "apiVersion": "run.googleapis.com/v1",
            "kind": "Job",
            "metadata": {
                "name": "vertflow-e2e-test-different-name",
                "annotations": {
                    "run.googleapis.com/launch-stage": "BETA",
                    "run.googleapis.com/execution-environment": "gen2",
                },
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "run.googleapis.com/launch-stage": "BETA",
                            "run.googleapis.com/execution-environment": "gen2",
                        }
                    },
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "image": "us-docker.pkg.dev/cloudrun/container/job:latest",
                                        "command": ["echo"],
                                        "args": ["Hello World - Different Command"],
                                        "env": [],
                                        "resources": {
                                            "limits": {"cpu": "1", "memory": "512Mi"}
                                        },
                                        "workingDir": "/",
                                        "ports": [{"containerPort": 8080}],
                                    }
                                ],
                                "maxRetries": 0,
                                "timeoutSeconds": "30",
                                "serviceAccountName": "empty-no-permissions@trading-nonprod.iam.gserviceaccount.com",
                            }
                        }
                    },
                }
            },
        }

    def test_basic(self) -> None:
        self.assertTrue(intersection_equal({}, {}))
        self.assertTrue(
            intersection_equal(
                {"a": {"aa": 11, "bb": 22}, "b": 2, "c": 3},
                {"a": {"aa": 11, "bb": 22}, "b": 2, "c": 3},
            )
        )
        self.assertFalse(
            intersection_equal(
                {"a": {"aa": 11, "bb": 22}, "b": 2, "c": 3},
                {"a": {"aa": 11, "bb": 22}, "b": 2, "c": 4},
            )
        )
        self.assertTrue(
            intersection_equal(
                {"a": {"aa": 11}, "bb": 22, "cc": 33},
                {"a": {"aa": 11, "bb": 22}, "b": 2, "c": 3},
            )
        )
        self.assertFalse(
            intersection_equal(
                {"a": {"aa": 44}, "b": 2, "c": 3},
                {"a": {"aa": 11, "bb": 22}, "b": 2, "c": 3},
            )
        )
        self.assertTrue(
            intersection_equal(
                {"a": {"aa": 11}, "b": 2, "c": 3}, {"a": {"bb": 22}, "b": 2, "c": 3}
            )
        )

    def test_spec_sent_and_received_are_equal(self) -> None:
        self.assertTrue(intersection_equal(self.spec_1_sent, self.spec_1_received))

    def test_spec_sent_and_different_spec_received_are_not_equal(self) -> None:
        self.assertFalse(intersection_equal(self.spec_2_sent, self.spec_1_received))
