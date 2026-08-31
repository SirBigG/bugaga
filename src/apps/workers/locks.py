import hashlib
from contextlib import contextmanager

from django.db import connection


def _lock_id(name):
    digest = hashlib.blake2b(name.encode(), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big", signed=True)


@contextmanager
def advisory_lock(name):
    if connection.vendor != "postgresql":
        yield True
        return

    lock_id = _lock_id(name)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s)", [lock_id])
        acquired = cursor.fetchone()[0]
    try:
        yield acquired
    finally:
        if acquired:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [lock_id])
