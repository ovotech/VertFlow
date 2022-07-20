from unittest import TestCase

from src.utils import intersection_equal


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
