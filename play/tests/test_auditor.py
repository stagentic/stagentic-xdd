import pytest

from auditor import Auditor


class TestAuditor:
    @pytest.fixture
    def evidence(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    def test_evaluate_returns_none_when_all_characteristics_pass(self, evidence):
        Auditor().evaluate(
            evidence=evidence,
            should=[
                {"characteristic": "always passes",
                 "verify": lambda transcript, working_dir: True,
                 "failure": "should never see this"},
            ],
        )

    @pytest.mark.parametrize(
        "evidence_text, working_dir_name", [
            ("hello agent", "workspace"),
            ("different transcript", "other-dir"),
        ],
        ids=["hello agent", "different transcript"]
    )
    def test_verify_receives_the_evidence_text_and_working_dir(self, evidence_text, working_dir_name, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(evidence_text)
        working_dir = tmp_path / working_dir_name

        seen = []

        def verification_spy(transcript, working_dir):
            seen.append((transcript, working_dir))
            return True

        Auditor().evaluate(
            evidence=transcript,
            working_dir=working_dir,
            should=[
                {"characteristic": "captures input",
                 "verify": verification_spy,
                 "failure": "n/a"},
            ],
        )

        assert seen == [(evidence_text, working_dir)]

    @pytest.mark.parametrize(
        "characteristic, failure", [
            ("my characteristic", "my failure message"),
            ("another characteristic", "another failure message"),
        ],
        ids=["my characteristic", "another characteristic"]
    )
    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, characteristic, failure, evidence):
        with pytest.raises(AssertionError) as excinfo:
            Auditor().evaluate(
                evidence=evidence,
                should=[
                    {"characteristic": characteristic,
                     "verify": lambda transcript, working_dir: False,
                     "failure": failure},
                ],
            )

        assert characteristic in str(excinfo.value)
        assert failure in str(excinfo.value)

    def test_failure_message_lists_every_failed_row(self, evidence):
        with pytest.raises(AssertionError) as excinfo:
            Auditor().evaluate(
                evidence=evidence,
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

        message = str(excinfo.value)
        assert "first characteristic" in message
        assert "first failure" in message

        assert "middle characteristic" not in message
        assert "middle failure" not in message

        assert "third characteristic" in message
        assert "third failure" in message
