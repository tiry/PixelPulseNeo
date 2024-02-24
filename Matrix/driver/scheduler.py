import os
import json
import logging
from typing import List
import shutil
import random
from datetime import datetime
from Matrix.driver.utilz import configure_log
from Matrix.models.Commands import CommandEntry, ScheduleModel, ScheduleCatalog
from Matrix.models.encode import deepcopy, loadModel
from Matrix.driver.base_executor import Base
from Matrix.driver import context

logger: logging.Logger = logging.getLogger(__name__)
configure_log(logger, level=logging.INFO)


class Scheduler(Base):
    def __init__(self, schedule_file: str | None = "schedule.json") -> None:
        self.schedule_file: str | None = schedule_file
        self.catalog: ScheduleCatalog | None = None
        if schedule_file is not None:
            logger.debug("loading schedule catalog")
            self.load()
        else:
            self.catalog = ScheduleCatalog()

        self.current_stack: ScheduleModel = ScheduleModel(commands=[])
        cname = self.get_next_catalog()
        if cname:
            self.load_playlist(cname)

    def make_empty(self) -> None:
        self.catalog = ScheduleCatalog()
        self.current_stack = ScheduleModel(commands=[])

    def get_valid_playlists(self) -> list[str]:
        result:list[str] = []

        if self.catalog is None:
            return result

        for name in self.catalog.playlists.keys():
            model: ScheduleModel = self.catalog.playlists[name]
            valid:bool = True
            if model.conditions is not None:
                for condition in model.conditions:
                    valid = valid and context.eval_condition(condition)
            if valid is True:
                result.append(name)
        return result
        
    def get_next_catalog(self) -> str | None:
        if self.catalog is None:
            return None
        valid_playlists: list[str] = self.get_valid_playlists()
        if len(valid_playlists)==0:
            if "default" in self.catalog.playlists.keys():
                return "default"
        elif len(valid_playlists)==1:
            return valid_playlists[0]
        else:
            return valid_playlists[random.randint(0, len(valid_playlists)-1)]
        return None

    def load(self, schedule_file: str | None = None) -> ScheduleCatalog | None:
        if not schedule_file:
            schedule_file = self.schedule_file
        if not schedule_file:
            logger.error("No schedule file to load")
            return
        if not os.path.exists(schedule_file):
            schedule_file = self.get_current_directory() + "/" + schedule_file

        logger.debug(f"loading schedule file {schedule_file}")
        self.catalog = None
        try:
            # logger.debug(f"loading schedule from file {schedule_file}")
            with open(schedule_file, "r") as file:
                self.catalog = loadModel(file.read(), ScheduleCatalog)
        except Exception as e:
            logger.error(f"Error loading schedule: {str(e)}")
            logger.error(e, exc_info=True)
        return self.catalog

    def save(self, schedule_file: str | None = None) -> None:
        if not schedule_file:
            schedule_file = self.schedule_file
        if not schedule_file:
            logger.error("No schedule file to save to")
            return
        if self.catalog is None:
            print("No schedule to save")
            return None

        if os.path.exists(schedule_file):
            # Create backup directory if it doesn't exist
            backup_dir: str = self.get_current_directory() + "/backups"
            # logger.debug(f"backup dir = {backup_dir}")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Get current timestamp for backup file name
            now: str = datetime.now().strftime("%Y%m%d%H%M%S")

            # Construct backup file path
            backup_file: str = backup_dir + "/schedule_" + now + ".bak"

            # Copy current schedule file to backup
            shutil.copy(schedule_file, backup_file)

            # Delete old backups, keeping last 5
            backup_files: list[str] = sorted(os.listdir(backup_dir))
            if len(backup_files) > 5:
                for old_file in backup_files[:-5]:
                    os.remove(backup_dir + "/" + old_file)

        # Save new schedule
        with open(schedule_file, "w") as file:
            json_str: str = self.catalog.model_dump_json()
            pretty: str = json.dumps(json.loads(json_str), indent=4)
            file.write(pretty)

    def get_current_stack(self) -> ScheduleModel | None:
        return self.current_stack

    def update_current_stack(self, schedule) -> None:
        self.current_stack = schedule

    def append_next(self, command_entry: CommandEntry):
        logger.debug("append command next")
        self.current_stack.commands.insert(0, command_entry)
        logger.debug(f"stack = => {self.current_stack.commands}")

    def append(self, command_entry: CommandEntry, before=None):
        if before:
            self.current_stack.commands.insert(before, command_entry)
        else:
            self.current_stack.commands.append(command_entry)

    def fetch_next_command(self):
        if len(self.current_stack.commands) == 0:
            cname = self.get_next_catalog()
            if cname:
                # logger.info(f"Reload Stack from schedule {cname}")
                self.load_playlist(cname)
            else:
                # logger.info("Empty stack and no default schedule => None Command returned")
                return None
        return self.current_stack.commands.pop(0)

    def create_playlist(self, name) -> ScheduleModel | None:
        if self.catalog is None:
            return None
        self.catalog.playlists[name] = deepcopy(self.current_stack)
        return self.get_playlist(name)

    def save_playlist(self, schedule, name) -> ScheduleModel | None:
        if self.catalog is None:
            return None
        self.catalog.playlists[name] = deepcopy(schedule)
        return self.get_playlist(name)

    def get_playlist_names(self) -> List[str]:
        if self.catalog is None:
            return []
        return [name for name in self.catalog.playlists.keys()]

    def get_playlists(self) -> list[ScheduleModel]:
        if self.catalog is None:
            return []
        return deepcopy(self.catalog.playlists)

    def get_playlist(self, name) -> ScheduleModel | None:
        if self.catalog is None:
            return None
        return self.catalog.playlists.get(name, None)

    def load_playlist(self, name) -> None:
        playlist: ScheduleModel | None = self.get_playlist(name)
        if playlist is None:
            logger.error(f"Playlist {name} not found")
            return None
        self.current_stack = ScheduleModel(commands=playlist.commands[:])
