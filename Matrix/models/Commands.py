from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime


class CommandEntry(BaseModel):
    command_name: str
    duration: float = 10.0
    args: List[str] = []
    kwargs: Dict[str, Any] = {}


class CommandExecutionLog(BaseModel):
    command: CommandEntry
    result: str|None
    error: Optional[str] = None
    execution_date: Optional[str] = datetime.now().strftime("%d/%m/%Y")
    execution_time: Optional[str] = datetime.now().strftime("%H:%M:%S")
    effective_duration: float


class ScheduleModel(BaseModel):
    commands: List[CommandEntry]
    conditions: Optional[List[str]] = []


class ScheduleCatalog(BaseModel):
    # playlists : dict = {} # ScheduleModel Map
    playlists: Dict[str, ScheduleModel] = {}  # ScheduleModel Map
