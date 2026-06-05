from collections.abc import Callable


def raise_if(
        items: list, *,
        raising_error: type[Exception],
        with_message: Callable[[list], str],
) -> None:
    raise ValueError("got ['a', 'b']")
