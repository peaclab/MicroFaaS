import logging as log
from threading import Event, Thread
from time import sleep
from typing import Any, Callable, NoReturn, Union

class FakeGPIO:
    """
    Adafruit GPIO stub class
    """
    # Dummy class variables
    OUT = "OUT"
    IN = "IN"
    HIGH = "HIGH"
    LOW = "LOW"

    def setup(pin, direction):
        log.debug("FakeGPIO: setup pin %s as %s", pin, direction)

    def output(pin, level):
        log.debug("FakeGPIO: output %s on pin %s", level, pin)

class IOEvent(Event):
    """Event with some conveinience methods for usage in a state machine"""

    def __init__(self, id: str) -> None:
        super().__init__()
        self.id = id
        self.value = None

    def set(self, value: Any = None) -> None:
        """
        Set the internal flag and (optionally) a value to be retrieved by wait() or
        wait_then_clear()
        """
        self.value = value
        super().set()

    def wait(self, timeout: int = None) -> Union[bool, Any]:
        """
        Block until internal flag is True or timeout. Return internal value (if set) or True.
        
        @throws TimeoutError if timeout occurs
        """
        if super().wait(timeout):
            return self.value if self.value is not None else True
        else:
            # Timeout
            raise TimeoutError

    def wait_then_clear(self, timeout: int = None) -> Union[bool, Any]:
        """
        Conveinience method: runs wait(), then clear(). Returns whatever wait() returned.

        @throws TimeoutError if timeout occurs
        """
        retval = self.wait(timeout)
        self.clear()
        return retval

    def clear(self) -> None:
        """
        Sets internal flag to False and internal value to None.
        """
        self.value = None
        super().clear()

    def __repr__(self) -> str:
        return self.__class__.__name__ + ":" + str(self.id)


class ActionableIOEvent(IOEvent):
    """IOEvent that runs an action in a separate thread upon set()"""

    def __init__(self, id: str, action: Callable[[], Any], holdoff: int = None):
        super().__init__(id)
        self._action = action
        self._holdoff = holdoff
        self._monitor_thread = Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def _monitor(self) -> NoReturn:
        if self._holdoff is not None:
            sleep(self._holdoff)

        while True:
            self.wait()
            try:
                self._action()
                self.clear()
            except Exception as ex:
                log.error("Action for %s threw exception: %s", self, ex)
                sleep(5)


class IOEventGroup():
    def __init__(self, id: str) -> None:
        self.id = id

    def __repr__(self) -> str:
        return self.__class__.__name__ + str(self.id)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value