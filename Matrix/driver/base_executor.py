import os
import json
from Matrix.driver.utilz import configure_log, BLUE
import logging
import json
import os
from datetime import datetime
import shutil
from Matrix.models.Commands import CommandEntry, ScheduleModel, ScheduleCatalog
from Matrix.models.encode import deepcopy, loadModel

BUFFER_SIZE = 1024*10    
    
class Base:

    def get_current_directory(self):
        return os.path.dirname(os.path.realpath(__file__))  


logger = logging.getLogger(__name__)
configure_log(logger, level = logging.INFO)

class Scheduler(Base):

    def __init__(self, schedule_file='schedule.json'):

        self.schedule_file = schedule_file
        if schedule_file!=None:
            logger.debug(f"loading schedule catalog")
            self.load()
        else:
            self.catalog = ScheduleCatalog()

        self.current_stack = ScheduleModel(commands=[])
        cname = self.get_next_catalog()
        if cname:
            self.load_playlist(cname)
    
    def make_empty(self):
         self.catalog = ScheduleCatalog()
         self.current_stack = ScheduleModel(commands=[])

    def get_next_catalog(self):
        if "default" in self.catalog.playlists.keys():
            return "default"
        return None

    def load(self, schedule_file=None):
        if not schedule_file:
            schedule_file = self.schedule_file
        if not os.path.exists(schedule_file):
            schedule_file = self.get_current_directory() + "/" + schedule_file
        
        logger.debug(f"loading schedule file {schedule_file}")
        self.catalog=None
        try:
            #logger.debug(f"loading schedule from file {schedule_file}")
            with open(schedule_file, 'r') as file:
                self.catalog = loadModel(file.read(), ScheduleCatalog)
        except Exception as e:
            logger.error(f"Error loading schedule: {str(e)}")
            logger.error(e, exc_info=True)  
        return self.catalog

    def save(self, schedule_file=None):
        if not schedule_file:
            schedule_file = self.schedule_file
        

        if  os.path.exists(schedule_file):           
            # Create backup directory if it doesn't exist
            backup_dir = self.get_current_directory() + "/backups"
            #logger.debug(f"backup dir = {backup_dir}")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Get current timestamp for backup file name
            now = datetime.now().strftime("%Y%m%d%H%M%S")

            # Construct backup file path
            backup_file = backup_dir + "/schedule_" + now + ".bak"

            # Copy current schedule file to backup
            shutil.copy(schedule_file, backup_file)

            # Delete old backups, keeping last 5
            backup_files = sorted(os.listdir(backup_dir))
            if len(backup_files) > 5:
                for old_file in backup_files[:-5]:
                    os.remove(backup_dir + "/" + old_file)

        # Save new schedule
        with open(schedule_file, 'w') as file:
            json_str = self.catalog.json()
            pretty = json.dumps(json.loads(json_str), indent=4)
            file.write(pretty)
  
    def get_current_stack(self):
        return self.current_stack
    
    def update_current_stack(self, schedule):
        self.current_stack = schedule

    def append_next(self, command_entry:CommandEntry):
        logger.debug("append command next")
        self.current_stack.commands.insert(0, command_entry)
        logger.debug(f"stack = => {self.current_stack.commands}")
        
         
    def append(self, command_entry:CommandEntry, before = None):
        if before:
            self.current_stack.commands.insert(before, command_entry)
        else:
            self.current_stack.commands.append(command_entry)

    def fetch_next_command(self):
        if len(self.current_stack.commands)==0:
            cname = self.get_next_catalog()
            if cname:
                #logger.info(f"Reload Stack from schedule {cname}")
                self.load_playlist(cname)
            else:
                #logger.info("Empty stack and no default schedule => None Command returned")
                return None
        return self.current_stack.commands.pop(0)

    def create_playlist(self, name):
        self.catalog.playlists[name] = deepcopy(self.current_stack)     
        return self.get_playlist(name)

    def save_playlist(self, schedule, name):
        self.catalog.playlists[name] = deepcopy(schedule)     
        return self.get_playlist(name)

    def get_playlist_names(self):
        return [name for name in self.catalog.playlists.keys()]

    def get_playlists(self):
        return deepcopy(self.catalog.playlists)
    
    def get_playlist(self, name):
        return self.catalog.playlists.get(name, None)

    def load_playlist(self,name):
        self.current_stack = ScheduleModel(commands = self.get_playlist(name).commands[:])
    

class BaseCommandExecutor(Base):
    
    def __init__(self):
        pass

    def list_commands(self):
        pass
    
    def get_commands(self):
        pass
    
    def get_command(self, name):
        pass

    def get_command_screenshot(self, name, screenshot_name):
        pass

    def list_schedules(self):
        pass

    def get_schedule(self, playlist_name):
        pass

    def set_schedule(self, schedule, playlist_name):
        pass

    def execute_now(self, command_name, duration, interrupt=False):
        pass

    def save_schedule(self):
        pass

    def stop(self,interrupt=False):
        pass


