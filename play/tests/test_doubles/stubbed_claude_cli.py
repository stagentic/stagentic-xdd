class StubbedClaudeCli:
    def __init__(self, response):
        self._response = response

    def __call__(self, prompt):
        return self._response
