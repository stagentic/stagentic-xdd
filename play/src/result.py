from dataclasses import dataclass


@dataclass
class Success[T]:
    value: T


@dataclass
class Failure[T]:
    value: T


type Result[T, E] = Success[T] | Failure[E]
