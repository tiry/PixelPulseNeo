import threading
import time
import queue
import json
import importlib
import os
import argparse

class CommandExecutor:

    def __init__(self, scheduler_enabled=True, schedule_file='schedule.json'):
        self.commands = self.load_commands()
        #print(f"loaded commands = {self.commands}")

        self.schedule_file = schedule_file
        self.schedule = []
        self.scheduler_enabled=scheduler_enabled
        if scheduler_enabled :
            self.schedule = self.load_schedule(self.schedule_file)
            print(f"loaded schedule = {self.schedule}")

        self.command_queue = queue.Queue()
        self.current_thread = None
        self.stop_current = threading.Event()
        self.schedule_thread = None
        if len(self.schedule)>0:
            print(f"starting schedule thread")
            self.schedule_thread = threading.Thread(target=self.run_schedule, args=())
            self.schedule_thread.start()

    def load_commands(self):
        commands = {}
        for file in os.listdir('commands'):
            if file.endswith('_cmd.py') and file != 'base.py':
                module_name = file[:-3]
                module = importlib.import_module(f'commands.{module_name}')
                class_name = f"{file[:-7].capitalize()}Cmd"
                command_class = getattr(module, class_name)
                command_instance = command_class()
                commands[command_instance.name] = command_instance
        return commands

    def load_schedule(self, schedule_file):
        try:
            with open(schedule_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading schedule: {str(e)}")
            return []

    def run_schedule(self):
        while not self.stop_current.is_set():
            for entry in self.schedule:    
                self.stop_current.set()
                if self.current_thread and self.current_thread.is_alive():
                    self.current_thread.join()
                self.execute_command(entry["command_name"], entry["duration"])
            self.stop_current.set()
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join()
            self.stop_current.clear()

    def execute_command(self, command_name, duration):
        self.stop_current.clear()
        command = self.commands.get(command_name)
        if command:
            self.current_thread = threading.Thread(target=self.run_command, args=(command,))
            self.current_thread.start()
            self.current_thread.join(timeout=duration)
            self.stop_current.set()
        else:
            print(f"Command {command_name} not found")

    def run_command(self, command):
        try:
            command.execute(self.stop_current)
        except Exception as e:
            print(f"Error executing {command.name}: {str(e)}")

    def execute_now(self, command_name, duration ):
        self.stop_current.set()
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join()
        if self.schedule_thread:
            self.schedule_thread.join()

        self.execute_command(command_name, duration)
        self.resume_schedule()

    def resume_schedule(self):
        if not self.scheduler_enabled: return
        self.schedule = self.load_schedule(self.schedule_file)
        if len(self.schedule)>0:
            self.schedule_thread.start()

    def stop(self):
        self.schedule_thread.join()




if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduler", help="start scheduler", action="store_true")
    parser.add_argument("-l", "--list", help="list commands", action="store_true")
   
    parser.add_argument("-d", "--duration", help="default command duration", default=5)
    parser.add_argument("-c", "--commands", nargs="+", help="list of commands to execute")
    
    args = parser.parse_args()
    
    #print(args.scheduler)
    #print(args.commands)
    
    executor = CommandExecutor(scheduler_enabled=args.scheduler)

    if args.list:
        print(f"Listing commands:")
        for command in executor.commands.values():
            print(f"{command.name} - {command.description}")
        exit(0)
 
    if args.commands:
        for command in args.commands:
            print(f"command = {command}")
            cmds = command.split(":")
            if len(cmds)==2:
                executor.execute_now(cmds[0], int(cmds[1]))
            else:
                executor.execute_now(cmds[0], int(args.duration))

    #executor.execute_now("time", 5)
    #executor.execute_now("meteo", 5)

    
    