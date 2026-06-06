from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest

from auditor import Auditor
from failure_message import formatted_failures_for


class TestAuditor:
    @pytest.fixture
    def evidence_source(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    @pytest.fixture
    def dummy_path(self): return Path("/dummy")

    class TestSucceeds:
        def test_evaluate_should_call_verify_with_evidence_text_and_working_dir(self, tmp_path):
            evidence_text = "hello agent"
            transcript = tmp_path / "transcript.md"
            transcript.write_text(evidence_text)
            working_dir = tmp_path / "workspace"
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                evidence_source=transcript,
                working_dir=working_dir,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
            )

            verify.assert_called_once_with(
                evidence_text, working_dir
            )

        def test_evaluate_should_pass_evidence_text_to_verify(self, tmp_path, dummy_path):
            evidence_text = "different transcript"
            transcript = tmp_path / "transcript.md"
            transcript.write_text(evidence_text)
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                evidence_source=transcript,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
                working_dir=dummy_path,
            )

            verify.assert_called_once_with(evidence_text, ANY)

        def test_evaluate_should_pass_working_dir_to_verify(self, evidence_source):
            working_dir = Path("/some/other/dir")
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                working_dir=working_dir,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
                evidence_source=evidence_source,
            )

            verify.assert_called_once_with(ANY, working_dir)

    class TestFails:
        def test_evaluation_should_fail_with_the_row_characteristic_and_failure(self, evidence_source, dummy_path):
            with pytest.raises(AssertionError) as excinfo:
                Auditor().evaluate(
                    should=[
                        {"characteristic": "my characteristic",
                         "verify": lambda transcript, working_dir: False,
                         "failure": "my failure message"},
                    ],
                    evidence_source=evidence_source, working_dir=dummy_path,
                )

            assert str(excinfo.value) == formatted_failures_for([
                {"characteristic": "my characteristic", "failure": "my failure message"}
            ])

        def test_evaluation_should_list_every_failed_row(self, evidence_source, dummy_path):
            with pytest.raises(AssertionError) as excinfo:
                Auditor().evaluate(
                    should=[
                        {"characteristic": "first characteristic",
                         "verify": lambda transcript, working_dir: False,
                         "failure": "first failure"},
                        {"characteristic": "middle characteristic",
                         "verify": lambda transcript, working_dir: True,
                         "failure": "middle failure"},
                        {"characteristic": "third characteristic",
                         "verify": lambda transcript, working_dir: False,
                         "failure": "third failure"},
                    ],
                    evidence_source=evidence_source, working_dir=dummy_path,
                )

            assert str(excinfo.value) == formatted_failures_for([
                {"characteristic": "first characteristic", "failure": "first failure"},
                {"characteristic": "third characteristic", "failure": "third failure"},
            ])

    class TestErrors:
        def test_evaluation_should_raise_when_the_scorecard_is_empty(self, dummy_path):
            with pytest.raises(ValueError, match="scorecard must not be empty"):
                Auditor().evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[],
                )
