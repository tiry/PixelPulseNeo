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
from Matrix.models.Commands import CommandEntry
from Matrix.driver.base_executor import Scheduler, BaseCommandExecutor,  BUFFER_SIZE
from Matrix.driver.ipc.server import IPCServer
from Matrix.models.Commands import CommandExecutionLog
from Matrix.driver.utilz import configure_log, CYAN
from Matrix.config import is_ipc_enabled

import logging

MAX_AUDIT_SIZE=100
BUSY_WAIT = 0.1

logger = logging.getLogger(__name__)
configure_log(logger, CYAN, "CmdExec")

class CommandExecutor(BaseCommandExecutor, IPCServer):

    def __init__(self, schedule_file='schedule.json'):

        # load commands
        self.commands = self._load_commands()

        # init scheduler and load playlists
        self.scheduler = Scheduler(schedule_file=schedule_file)
        
        self.stop_current = threading.Event()
        self.stop_scheduler = threading.Event()
        self.schedule_thread = None
        print(f"starting schedule thread")
        self.schedule_thread = threading.Thread(target=self._scheduler_loop, args=())
        self.schedule_thread.start()

        self.audit_log = []
        self.execution_counter=0

    def _load_commands(self):
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
        return list(self.commands.keys())
    
    def get_commands(self):
        result = []
        for name in self.commands:
            result.append(self.get_command(name))
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
    
    def _load_schedule(self, name):
        self.scheduler.load_playlist(name)

    def get_schedule(self, name = None):
        if name is None:
            return self.scheduler.get_current_stack()
        else:
            return self.scheduler.get_playlist(name)
    
    def list_schedules(self):
        return self.scheduler.get_playlist_names()

    def set_schedule(self, schedule, name= None):
        if name:
            self.scheduler.save_playlist(schedule, name)
        else:
            self.scheduler.update_current_stack(schedule)

    def save_schedule(self, schedule_file=None):
        self.scheduler.save(schedule_file=schedule_file)

    def _scheduler_loop(self):
        while not self.stop_scheduler.is_set():
            command_entry  = self.scheduler.fetch_next_command()
            if not self.stop_scheduler.is_set():
                if command_entry:
                    self._run_command(command_entry)
                else:
                    time.sleep(BUSY_WAIT)
        print("SCHEDULER EXITED FOR REAL")

    def _add_log(self, log_entry):
        logger.debug(f" [AUDIT] {log_entry}")
        self.audit_log.append(log_entry)
        if len(self.audit_log)>MAX_AUDIT_SIZE:
            try:
                self.audit_log.remove(0)
            except Exception as e :
                pass

    def _log_exec(self,log_entry):
        self._add_log(log_entry)
        self.execution_counter +=1 # unbounded int in python3


    def get_audit_log(self):
        return self.audit_log

    def get_execution_count(self):
        return self.execution_counter

    def _wait_for_executions(self, num_executions, timeout_seconds=10):
        t0=time.time()
        c0=self.get_execution_count()
        while((time.time()-t0) < timeout_seconds):
            time.sleep(BUSY_WAIT)
            c_now = self.get_execution_count()
            if c_now-c0 >= num_executions:
                break
        return self.get_audit_log()[:]       


    def _run_command(self, command_entry):
        try:
            self.stop_current.clear()
            executable_command = self.commands.get(command_entry.command_name)

            t0 = time.time()
            res, err = executable_command.execute(self.stop_current, command_entry.duration, command_entry.args, command_entry.kwargs )
            logger.debug(f"run_command executed with result = {res} and error = {err}")
            error = None
            if err:
                error = str(err)

            log_entry = CommandExecutionLog(command=command_entry.copy(deep=True), result=str(res), effective_duration=time.time()-t0, error=error)
            self._log_exec(log_entry)

        except Exception as e:
            logger.error(f"Error executing {command_entry.command_name}: {str(e)}")
            logger.error(traceback.format_exc())
            log_entry = CommandExecutionLog(command=command_entry.copy(deep=True), result=None, effective_duration=time.time()-t0, error=str(e))
            self._add_log(log_entry)


    def execute_now(self, command_name, duration , args = [], kwargs = {}, interrupt=False):
        self.scheduler.append_next(CommandEntry(command_name=command_name, duration=duration, args=args, kwargs=kwargs))
        if interrupt:
            self.stop_current.set()

    def stop(self, interrupt=False):
        logger.info("Stop request received")
        
        self.stop_scheduler.set()
        time.sleep(BUSY_WAIT*5)
        if (interrupt):
            self.stop_current.set()
            time.sleep(BUSY_WAIT*5)
        logger.debug("waiting for scheduler thread to exit")
        self.schedule_thread.join(timeout=2)
        logger.info("Scheduler shutdown completed, exiting")

    def get_valid_commands(self):
        # make remote commands list explicit
        return {
            "ls": self.list_commands,
            "get_commands": self.get_commands,
            "get_command": self.get_command,
            "get_command_screenshot" : self.get_command_screenshot,
            "list_schedules" : self.list_schedules,
            "get_schedule" : self.get_schedule,
            "execute_now" : self.execute_now,
            "set_schedule" : self.set_schedule,
            "save_schedule" : self.save_schedule,
            "stop" : self.stop,
            
        }


###################################
# Helper to manage as singleton
singleton=None
def instance():
    global singleton

    if not singleton:
        singleton = CommandExecutor()
    return singleton

def release():
    global singleton

    if singleton:
        singleton = None
    
def client():
    global singleton
    if not singleton:
        singleton = None
    return singleton

if __name__ == "__main__":

    ###################################
    # act as a simple CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduler", help="start scheduler", action="store_true")
    parser.add_argument("-l", "--list", help="list commands", action="store_true")
    parser.add_argument("-s", "--listen", help="start IPC Server", action="store_true")
   
    parser.add_argument("-d", "--duration", help="default command duration", default=5)
    parser.add_argument("-c", "--commands", nargs="+", help="list of commands to execute")
    
    args = parser.parse_args()
    
    if not args.scheduler:
        # prevent loading of default scheduler file
        executor = CommandExecutor(schedule_file=None)
    else:
        executor = CommandExecutor()

    if args.list:
        print(f"Listing commands:")
        for command in executor.commands.values():
            print(f"{command.name} - {command.description}")
        #exit(0)
 
    if args.listen or is_ipc_enabled():
        executor.serve()    
    else:
        if args.commands:
            for command in args.commands:
                print(f"command = {command}")
                cmds = command.split(":")
                if len(cmds)==2:
                    executor.execute_now(cmds[0], int(cmds[1]))
                else:
                    executor.execute_now(cmds[0], int(args.duration))
                time.sleep(1)
    executor.stop()
    
    