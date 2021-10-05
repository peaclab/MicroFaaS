from threading import Event, Lock
from collections import deque


class FIFOLock(object):
    """
    FIFO-ordered "fair" lock; i.e., if multiple threads are queuing for a lock, the thread that
    blocked first will get the lock next. Adapted from vitaliyp/fifo_lock.py:
    https://gist.github.com/vitaliyp/6d54dd76ca2c3cdfc1149d33007dc34a
    """

    def __init__(self):
        self._lock = Lock()
        self._inner_lock = Lock()
        self._pending_threads = deque()

    def locked(self):
        return self._lock.locked()

    def acquire(self, blocking=True):
        with self._inner_lock:
            lock_acquired = self._lock.acquire(False)
            if lock_acquired:
                return True
            elif not blocking:
                return False

            release_event = Event()
            self._pending_threads.append(release_event)

        release_event.wait()
        return self._lock.acquire()

    def release(self):
        with self._inner_lock:
            if self._pending_threads:
                release_event = self._pending_threads.popleft()
                release_event.set()

            self._lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, t, v, tb):
        self.release()