from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class CommandEntry(BaseModel):
    command_name: str
    duration: float = 10.0
    args: List[str] = []
    kwargs: Dict[str, str] = {}

class CommandExecutionLog(BaseModel):

    command : CommandEntry
    result : str
    error: Optional[str] = None 
    execution_date: Optional[str] = datetime.now().strftime("%d/%m/%Y")
    execution_time: Optional[str] = datetime.now().strftime("%H:%M:%S")
    effective_duration : float

datetime.now().strftime("%H:%M:%S")
class Schedule(BaseModel):

    commands : List[CommandEntry]
    conditions : Optional[List[str]] = []

class ScheduleCatalog(BaseModel):

    playlists : dict = {} # Schedule Map
