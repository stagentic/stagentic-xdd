from dataclasses import dataclass


@dataclass
class Success:
    value: object


class Failure:
    def __init__(self, value):
        self.value = value
