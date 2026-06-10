from dataclasses import dataclass

type Result[T, E] = Success[T] | Failure[E]


@dataclass
class Success[T]: value: T


@dataclass
class Failure[T]: value: T
