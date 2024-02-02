from pydantic import BaseModel
from typing import List, Dict, Optional

class CommandEntry(BaseModel):
    command_name: str
    duration: int = 10
    args: List[str] = []
    nargs: Dict[str, str] = {}

class Schedule(BaseModel):

    commands : List[CommandEntry]
    conditions : Optional[List[str]] = []

class ScheduleCatalog(BaseModel):

    playlists : dict = {} # Schedule Map
