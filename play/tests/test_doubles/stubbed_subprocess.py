from dataclasses import dataclass


@dataclass
class _Result:
    returncode: int
    stdout: str
    stderr: str


class StubbedSubprocess:
    def __init__(self, *, returncode=0, stdout="", stderr=""):
        self._result = _Result(returncode=returncode, stdout=stdout, stderr=stderr)

    def __call__(self, cmd, **kwargs):
        return self._result
