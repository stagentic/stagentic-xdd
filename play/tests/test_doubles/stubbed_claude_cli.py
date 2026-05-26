class StubbedClaudeCli:
    def __init__(self, response):
        self._response = response

    def __call__(self, prompt, *, workspace=None):
        return self._response
