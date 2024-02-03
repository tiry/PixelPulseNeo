import threading
import time
import queue
import json
import importlib
import os
import argparse
from datetime import datetime
import shutil
import time
import traceback
from Matrix.models.Commands import CommandEntry, Schedule
from Matrix.driver.base_executor import Scheduler, BaseCommandExecutor,  BUFFER_SIZE
from Matrix.driver.ipc_server import IPCServer
from Matrix.models.Commands import CommandExecutionLog

MAX_AUDIT_SIZE=100
BUSY_WAIT = 0.1


from Matrix.driver.utilz import configure_log, CYAN
import logging

logger = logging.getLogger(__name__)
configure_log(logger, CYAN, "CmdExec")


class CommandExecutor(BaseCommandExecutor, IPCServer):

    def __init__(self, schedule_file='schedule.json'):

        # load commands
        self.commands = self.load_commands()

        # init scheduler and load playlists
        self.scheduler = Scheduler(schedule_file=schedule_file)
        
        self.stop_current = threading.Event()
        self.stop_scheduler = threading.Event()
        self.schedule_thread = None
        print(f"starting schedule thread")
        self.schedule_thread = threading.Thread(target=self._scheduler_loop, args=())
        self.schedule_thread.start()

        self.audit_log = []

    def load_commands(self):
        commands = {}
        current_directory = self.get_current_directory()
        for file in os.listdir(f'{current_directory}/commands'):
            if file.endswith('_cmd.py') and file != 'base.py':
                try:
                    module_name = file[:-3]
                    module = importlib.import_module(f'Matrix.driver.commands.{module_name}')
                    class_name = f"{file[:-7].capitalize()}Cmd"
                    command_class = getattr(module, class_name)
                    command_instance = command_class()
                    commands[command_instance.name] = command_instance
                except Exception as e:
                    logger.error(f"ERROR >> Unable to load command {command_class}]")
                    logger.error(traceback.format_exc())
        return commands

    def list_commands(self):
        return self.commands.keys()
    
    def get_commands(self):
        result = []
        for name in self.commands:
            cmd = self.commands[name]
            result.append({
                "name": cmd.name,
                "description": cmd.description,
                "screenshots": cmd.getScreenShots()
            })
        return result
    
    def get_command(self, name):
        cmd = self.commands.get(name, None)
        if cmd:
            return {
                "name": cmd.name,
                "description": cmd.description,
                "screenshots": cmd.getScreenShots()
            }
        return None

    def get_command_screenshot(self, name, screenshot_name):
        cmd = self.commands.get(name, None)
        if cmd:
            return cmd.getScreenShot(screenshot_name)
        return None
    
    def get_schedule(self):
        return self.scheduler.get_current_stack()

    def set_schedule(self, schedule):
        # XXX
        self.scheduler

    def save_schedule(self, schedule_file=None):
        self.scheduler.save(schedule_file=schedule_file)

    def _scheduler_loop(self):
        while not self.stop_scheduler.is_set():
            command_entry  = self.scheduler.fetch_next_command()
            if command_entry:
                self._run_command(command_entry)
            else:
                time.sleep(BUSY_WAIT)

    def _add_log(self, log_entry):
        print(f"LOG> {log_entry}")
        self.audit_log.append(log_entry)
        if len(self.audit_log)>MAX_AUDIT_SIZE:
            self.audit_log.remove(0)

    def get_audit_log(self):
        return self.audit_log

    def _run_command(self, command_entry):
        try:
            self.stop_current.clear()
            executable_command = self.commands.get(command_entry.command_name)

            t0 = time.time()
            res, err = executable_command.execute(self.stop_current, command_entry.duration, command_entry.args, command_entry.kwargs )
            print(f"run_command executed with result = {res} and error = {err}")
            error = None
            if err:
                error = str(err)

            log_entry = CommandExecutionLog(command=command_entry.copy(deep=True), result=str(res), effective_duration=time.time()-t0, error=error)
            self._add_log(log_entry)

        except Exception as e:
            print(f"Error executing {command_entry.command_name}: {str(e)}")
            print(traceback.format_exc())
            log_entry = CommandExecutionLog(command=command_entry.copy(deep=True), result=None, effective_duration=time.time()-t0, error=str(e))
            self._add_log(log_entry)


    def execute_now(self, command_name, duration , args = [], kwargs = {}, interrupt=False):
        self.scheduler.append_next(CommandEntry(command_name=command_name, duration=duration, args=args, kwargs=kwargs))
        if interrupt:
            self.stop_current.set()

    def stop(self):
        time.sleep(0.1)
        self.stop_scheduler.set()
        self.schedule_thread.join()

    def execute_ipc_request(self, command, args, kwargs):
        response_wrapper = {
            "success" : False,
            "error": None,
            "response" : None
        }
        try:
            if command =="list_commands":
                response = self.list_commands()
                response_wrapper["success"]=True
                response_wrapper["response"] = response
            elif command =="get_commands":
                response = self.get_commands()
                response_wrapper["success"]=True
                response_wrapper["response"] = response
            else:
                response_wrapper["error"]=f"Command {command} not found"
        except Exception as e:
            response_wrapper["success"]=False
            response_wrapper["error"] = str(e)
            print(e)
        
        return response_wrapper


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduler", help="start scheduler", action="store_true")
    parser.add_argument("-l", "--list", help="list commands", action="store_true")
    parser.add_argument("-s", "--listen", help="start IPC Server", action="store_true")
    
   
    parser.add_argument("-d", "--duration", help="default command duration", default=5)
    parser.add_argument("-c", "--commands", nargs="+", help="list of commands to execute")
    
    args = parser.parse_args()
    
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
    
    