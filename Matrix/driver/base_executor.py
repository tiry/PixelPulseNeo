import logging
from threading import Lock, RLock
from functools import wraps
import os
from abc import ABC, abstractmethod
from Matrix.driver.utilz import configure_log

BUFFER_SIZE = 1024 * 10

logger = logging.getLogger(__name__)
configure_log(logger, level=logging.INFO)


def synchronized_method(method):
    """Decorator to lock and synchronize methods across threads."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_lock'):
            self._lock = RLock()
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper

class Base:
    """
    Shared Base Class used to share some utility code
    """

    def get_current_directory(self):
        return os.path.dirname(os.path.realpath(__file__))

class BaseCommandExecutor(ABC, Base):
    """
    Base Class for Command Executor : defines the expected interface

    Args:
        ABC (_type_): _description_
        Base (_type_): _description_
    """
    def __init__(self):
        pass

    @abstractmethod
    def list_commands(self):
        pass

    @abstractmethod
    def get_commands(self):
        pass

    @abstractmethod
    def get_command(self, name):
        pass

    @abstractmethod
    def get_command_screenshot(self, name, screenshot_name):
        pass

    @abstractmethod
    def list_schedules(self):
        pass

    @abstractmethod
    def get_schedule(self, playlist_name):
        pass

    @abstractmethod
    def set_schedule(self, schedule, playlist_name):
        pass

    @abstractmethod
    def execute_now(self, command_name, duration, interrupt=False, args=[], kwargs={}):
        pass

    @abstractmethod
    def save_schedule(self):
        pass

    @abstractmethod
    def stop(self, interrupt=False):
        pass

    @abstractmethod
    def connected(self):
        pass
    