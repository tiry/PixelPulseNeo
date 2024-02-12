import threading
from Matrix.driver.executor import CommandExecutor
from Matrix.driver.ipc.client import IPCClientExecutor

class CommandExecutorSingleton:
    """
    Wrap the CommandExecutor Class to provide a singleton in a threadsafe manner
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = CommandExecutor()
        return cls._instance
    
    @classmethod
    def release(cls):
        with cls._lock:
            cls.instance = None


class IPCClientSingleton:
    """
    Wrap the IPCClientExecutor Class to provide a singleton in a threadsafe manner
    """

    _instance = None
    _lock = threading.Lock()

    start_server_if_needed=False

    @classmethod
    def instance(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = IPCClientExecutor(False, start_server_if_needed=cls.start_server_if_needed)
        return cls._instance
    
    @classmethod
    def release(cls):
        with cls._lock:
            cls.instance = None


