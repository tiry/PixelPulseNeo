import logging
from threading import RLock
from functools import wraps
import os
from typing import List, Dict
from abc import ABC, abstractmethod
from Matrix.driver.utilz import configure_log
from Matrix.models.Commands import ScheduleModel
import traceback

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
            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                logger.error("Exception in synchronized method ")
                print(f"args = {args} ")
                print(f"kwargs = {kwargs} ")
                traceback.print_exc()
                raise e
            
    return wrapper

class Base:
    """
    Shared Base Class used to share some utility code
    """

    def get_current_directory(self) -> str:
        return os.path.dirname(os.path.realpath(__file__))
    
class BaseCommandExecutor(ABC, Base):
    """
    Base Class for Command Executor : defines the expected interface

    Args:
        ABC (_type_): _description_
        Base (_type_): _description_
    """
    
    def __init__(self):
        """
        Constructor method
        """
        pass

    @abstractmethod
    def list_commands(self) -> List[str]:
        """
        List all registered available commands
        
        Returns:
            List[str]: List of command names
        """
        pass

    @abstractmethod
    def get_commands(self) -> list(Dict[str,str]):
        """
        Get all available commands
        
        Returns:
           Dict[str, Command]: Dictionary of command name to command object
        """
        pass

    @abstractmethod
    def get_command(self, name: str) -> Dict[str,str]:
        """
        Get a command by name
        
        Args:
            name (str): Name of the command
            
        Returns:
            Command: Command object 
        """
        pass

    @abstractmethod
    def get_command_screenshot(self, name: str, screenshot_name: str) -> str:
        """
        Get a screenshot for a command
        
        Args:
            name (str): Name of the command
            screenshot_name (str): name of the screenshot
        """
        pass

    @abstractmethod
    def list_schedules(self) -> list[str]:
        """
        List all scheduled playlists
        
        Returns:
            List[str]: List of playlist names
        """
        pass

    @abstractmethod
    def get_schedule(self, playlist_name: str) -> ScheduleModel:
        """
        Get a playlist schedule
        
        Args:
            playlist_name (str): Name of the playlist
            
        Returns:
            Schedule: Schedule object
        """
        pass

    @abstractmethod
    def set_schedule(self, schedule: ScheduleModel, playlist_name: str) -> None:
        """
        Set a playlist schedule
        
        Args:
            schedule (Schedule): Schedule object
            playlist_name (str): Name of the playlist
        """
        pass

    @abstractmethod
    def execute_now(self, command_name: str, duration: int, interrupt: bool = False, args: List = [], kwargs: Dict = {}) -> None:
        """
        Execute a command immediately
        
        Args:
            command_name (str): Name of the command
            duration (int): Duration in seconds
            interrupt (bool): Interrupt current command
            args (List): Positional arguments
            kwargs (Dict): Keyword arguments
        """
        pass

    @abstractmethod
    def save_schedule(self) -> None:
        """
        Save current schedule to disk
        """
        pass

    @abstractmethod
    def stop(self, interrupt: bool = False) -> None:
        """
        Stop the CommandExecutor
        
        Args:
            interrupt (bool): Force stop by interrupting
        """
        pass

    @abstractmethod
    def connected(self) -> bool:
        """
        Check if executor is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass

