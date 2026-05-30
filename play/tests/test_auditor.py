import pytest
from unittest.mock import MagicMock

from auditor import Auditor


class TestAuditor:
    @pytest.fixture
    def evidence(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    @pytest.fixture
    def working_dir(self, tmp_path):
        return tmp_path

    def test_evaluation_should_raise_when_the_scorecard_is_empty(self, evidence, working_dir):
        with pytest.raises(ValueError, match="scorecard must not be empty"):
            Auditor().evaluate(
                evidence=evidence,
                working_dir=working_dir,
                should=[],
            )

    @pytest.mark.parametrize(
        "evidence_text, working_dir_name", [
            ("hello agent", "workspace"),
            ("different transcript", "other-dir"),
        ],
        ids=["hello agent", "different transcript"]
    )
    def test_verify_should_receive_the_evidence_text_and_working_dir(self, evidence_text, working_dir_name, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(evidence_text)
        working_dir = tmp_path / working_dir_name

        verify = MagicMock(return_value=True)

        Auditor().evaluate(
            evidence=transcript,
            working_dir=working_dir,
            should=[
                {"characteristic": "captures input",
                 "verify": verify,
                 "failure": "n/a"},
            ],
        )

        verify.assert_called_once_with(evidence_text, working_dir)

    def test_evaluation_should_not_raise_when_all_characteristics_pass(self, evidence, working_dir):
        Auditor().evaluate(
            evidence=evidence,
            working_dir=working_dir,
            should=[
                {"characteristic": "always passes",
                 "verify": lambda transcript, working_dir: True,
                 "failure": "should never see this"},
                {"characteristic": "also always passes",
                 "verify": lambda transcript, working_dir: True,
                 "failure": "should never see this either"},
            ],
        )

    @pytest.mark.parametrize(
        "characteristic, failure", [
            ("my characteristic", "my failure message"),
            ("another characteristic", "another failure message"),
        ],
        ids=["my characteristic", "another characteristic"]
    )
    def test_failure_message_should_carry_the_row_characteristic_and_failure_when_a_row_fails(self, characteristic, failure, evidence, working_dir):
        with pytest.raises(AssertionError) as excinfo:
            Auditor().evaluate(
                evidence=evidence,
                working_dir=working_dir,
                should=[
                    {"characteristic": characteristic,
                     "verify": lambda transcript, working_dir: False,
                     "failure": failure},
                ],
            )

        assert str(excinfo.value) == f"- {characteristic}: {failure}"

    def test_failure_message_should_list_every_failed_row(self, evidence, working_dir):
        with pytest.raises(AssertionError) as excinfo:
            Auditor().evaluate(
                evidence=evidence,
                working_dir=working_dir,
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
            )

        assert str(excinfo.value) == (
            "- first characteristic: first failure\n"
            "- third characteristic: third failure"
        )
