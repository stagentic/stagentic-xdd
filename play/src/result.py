from dataclasses import dataclass


@dataclass
class Success:
    value: object


@dataclass
class Failure:
    value: object
