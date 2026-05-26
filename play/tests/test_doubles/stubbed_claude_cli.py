class StubbedClaudeCli:
    def __init__(self, response):
        self._response = response

    def __call__(self, prompt, **kwargs):
        return self._response
