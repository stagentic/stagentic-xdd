class ClaudeCli:
    def __init__(self, subprocess=None):
        self._subprocess = subprocess

    def __call__(self, prompt):
        raise NotImplementedError
