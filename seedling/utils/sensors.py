import random, time
from typing import TypeVar, Callable

T = TypeVar('T')


class RecoverableSensorError(Exception):
    pass


class UnRecoverableSensorError(Exception):
    pass


def retry_with_backoff(fn: Callable[[], T], retries=5, backoff_in_seconds=1) -> T:
    x = 0
    while True:
        try:
            return fn()
        except RecoverableSensorError as exc:
            if x == retries:
                raise UnRecoverableSensorError(str(exc))
            sleep = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
            time.sleep(sleep)
            x += 1
