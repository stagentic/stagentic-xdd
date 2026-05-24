import re
import shutil
from pathlib import Path

TASKS = Path(__file__).parent.parent / "tasks"


def test_write_a_failing_test(tmp_path):
    fixture = tmp_path / "miles-to-km"
    shutil.copytree(TASKS / "0-placeholder" / "expected", fixture)
    task = TASKS / "1-first-test-for-miles-to-km-converter"

    transcript_path = _fake_agent_performs(
        task=task,
        in_workspace=fixture
    )

    _audit(
        expecting=_characteristics(fixture, task, by=[
            "Production module exists at src/conversion.py with content",
            "Workspace state matches the expected end-state (src, tests, transcript)",
            "Transcript shows the agent ran pytest",
            "Transcript shows a FAILED pytest result",
            "First test fails for the right reason",
        ]),
        transcript_path=transcript_path,
    )


def _fake_agent_performs(*, task, in_workspace):
    shutil.copytree(task / "expected", in_workspace, dirs_exist_ok=True)
    return in_workspace / "transcript.md"


def _characteristics(fixture, task, *, by):
    table = {
        "Production module exists at src/conversion.py with content": {
            "verify": lambda transcript: (
                (fixture / "src" / "conversion.py").is_file()
                and (fixture / "src" / "conversion.py").stat().st_size > 0
            ),
            "failure": "src/conversion.py is missing or empty",
        },
        "Workspace state matches the expected end-state (src, tests, transcript)": {
            "verify": lambda transcript: not _tree_diff(task / "expected", fixture),
            "failure": "workspace contents do not match the expected end-state",
        },
        "Transcript shows the agent ran pytest": {
            "verify": lambda transcript: bool(
                re.search(r"\[TOOL\] \*\*Bash\*\*.*?pytest", transcript, re.DOTALL)
            ),
            "failure": "transcript shows no `[TOOL] **Bash**` running pytest",
        },
        "Transcript shows a FAILED pytest result": {
            "verify": lambda transcript: bool(
                re.search(r"\[TOOL\] \*\*Bash\*\*.*?pytest.*?FAILED", transcript, re.DOTALL)
            ),
            "failure": "transcript shows no FAILED result from pytest",
        },
        "First test fails for the right reason": {
            "verify": lambda transcript: (
                bool(re.search(r"FAILED.*?(assert|AssertionError)", transcript, re.DOTALL))
                and not re.search(
                    r"(ImportError|NameError|ModuleNotFoundError|cannot import name)",
                    transcript, re.DOTALL,
                )
            ),
            "failure": "assertion not against a stub (type default or input echoed); got a missing-function error instead",
        },
    }
    return [{"characteristic": name, **table[name]} for name in by]


def _audit(expecting, *, transcript_path):
    transcript = transcript_path.read_text()
    failures = [row for row in expecting if not row["verify"](transcript)]
    if not failures:
        return
    msg = "Failed characteristics:"
    for row in failures:
        msg += f"\n  - {row['characteristic']}"
        msg += f"\n      {row['failure']}"
    raise AssertionError(msg)


def _tree_diff(expected_root, actual_root):
    expected = {p.relative_to(expected_root): p for p in expected_root.rglob("*") if p.is_file()}
    actual = {p.relative_to(actual_root): p for p in actual_root.rglob("*") if p.is_file()}
    diffs = []
    for rel in sorted(set(expected) | set(actual), key=str):
        if rel not in expected:
            diffs.append(f"unexpected: {rel}")
        elif rel not in actual:
            diffs.append(f"missing: {rel}")
        elif expected[rel].read_bytes() != actual[rel].read_bytes():
            diffs.append(f"differs: {rel}")
    return diffs
