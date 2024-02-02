import os

BUFFER_SIZE = 1024*10


class BaseCommandExecutor:

    def get_current_directory(self):
        return os.path.dirname(os.path.realpath(__file__))  

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

    def load_schedule(self, schedule_file=None):
        pass

    def get_schedule(self):
        pass

    def set_schedule(self, schedule):
        pass

    def run_command(self, command):
        pass

    def run_schedule(self):
        pass

