import logging
from typing import Any, Callable
import threading
import time
import importlib
import os
import argparse
import traceback
from Matrix.models.Commands import CommandEntry
from Matrix.driver.base_executor import BaseCommandExecutor, synchronized_method
from Matrix.driver.scheduler import Scheduler
from Matrix.driver.ipc.server import IPCServer
from Matrix.models.Commands import CommandExecutionLog
from Matrix.driver.utilz import configure_log, CYAN
from Matrix.config import is_ipc_enabled
from Matrix.models.Commands import ScheduleModel, CommandEntry, ScheduleCatalog

MAX_AUDIT_SIZE = 100
BUSY_WAIT = 0.1

logger: logging.Logger = logging.getLogger(__name__)
configure_log(logger, CYAN, "CmdExec")


class CommandExecutor(BaseCommandExecutor, IPCServer):

    def __init__(self, schedule_file:str | None ="schedule.json"):
        # load commands
        self.commands:dict[str, Any] = self._load_commands()

        # init scheduler and load playlists
        self.scheduler = Scheduler(schedule_file=schedule_file)

        self.stop_current = threading.Event()
        self.stop_scheduler = threading.Event()
        self.schedule_thread: threading.Thread | None = None
        print("starting schedule thread")
        self.schedule_thread = threading.Thread(target=self._scheduler_loop, args=())
        self.schedule_thread.start()

        self.audit_log:list[CommandExecutionLog] = []
        self.execution_counter = 0

    def _load_commands(self) -> dict:
        commands: dict[str, Any] = {}
        current_directory: str = self.get_current_directory()
        for file in os.listdir(f"{current_directory}/commands"):
            if file.endswith("_cmd.py") and file != "base.py":
                try:
                    module_name: str = file[:-3]
                    module = importlib.import_module(
                        f"Matrix.driver.commands.{module_name}"
                    )
                    class_name: str = f"{file[:-7].capitalize()}Cmd"
                    command_class = getattr(module, class_name)
                    command_instance = command_class()
                    commands[command_instance.name] = command_instance
                except Exception:
                    logger.error(f"ERROR >> Unable to load command {command_class}]")
                    logger.error(traceback.format_exc())
        return commands

    @synchronized_method
    def list_commands(self) -> list[str]:
        return list(self.commands.keys())

    @synchronized_method
    def get_commands(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for name in self.commands:
            res: dict[str, Any] | None = self.get_command(name)
            if res:
                result.append(res)
        return result

    @synchronized_method
    def get_command(self, name)-> dict[str, Any] | None:
        cmd = self.commands.get(name, None)
        if cmd:
            return {
                "name": cmd.name,
                "description": cmd.description,
                "screenshots": cmd.get_screenshots(),
            }
        return None
        
    @synchronized_method
    def get_command_screenshot(self, name, screenshot_name) -> str | None:
        cmd = self.commands.get(name, None)
        if cmd:
            return cmd.get_screenshot(screenshot_name)
        return None

    def _load_schedule(self, name) -> None:
        self.scheduler.load_playlist(name)

    @synchronized_method
    def get_schedule(self, playlist_name:str|None=None) -> ScheduleModel | None:
        if playlist_name is None:
            return self.scheduler.get_current_stack()
        else:
            return self.scheduler.get_playlist(playlist_name)

    @synchronized_method
    def list_schedules(self) -> list[str]:
        return self.scheduler.get_playlist_names()

    @synchronized_method
    def set_schedule(self, schedule:ScheduleModel, playlist_name:str|None =None) -> None:
        if playlist_name is not None:
            self.scheduler.save_playlist(schedule, playlist_name)
        else:
            self.scheduler.update_current_stack(schedule)

    @synchronized_method
    def save_schedule(self, schedule_file=None):
        self.scheduler.save(schedule_file=schedule_file)

    def _scheduler_loop(self) -> None:
        while not self.stop_scheduler.is_set():
            command_entry: CommandEntry | None = self.scheduler.fetch_next_command()
            if not self.stop_scheduler.is_set():
                if command_entry:
                    self._run_command(command_entry)
                else:
                    time.sleep(BUSY_WAIT)
        print("SCHEDULER EXITED FOR REAL")

    def _add_log(self, log_entry: CommandExecutionLog) -> None:
        logger.debug(f" [AUDIT] {log_entry}")
        self.audit_log.append(log_entry)
        if len(self.audit_log) > MAX_AUDIT_SIZE:
            try:
                self.audit_log.pop(0)
            except Exception:
                pass

    def _log_exec(self, log_entry:CommandExecutionLog) -> None:
        self._add_log(log_entry)
        self.execution_counter += 1  # unbounded int in python3

    def get_audit_log(self) -> list[CommandExecutionLog]:
        return self.audit_log

    def get_execution_count(self) -> int:
        return self.execution_counter

    def _wait_for_executions(self, num_executions, timeout_seconds=10) -> list[CommandExecutionLog]:
        t0: float = time.time()
        c0: int = self.get_execution_count()
        while (time.time() - t0) < timeout_seconds:
            time.sleep(BUSY_WAIT)
            c_now: int = self.get_execution_count()
            if c_now - c0 >= num_executions:
                break
        return self.get_audit_log()[:]

    def _run_command(self, command_entry):
        try:
            self.stop_current.clear()
            executable_command: Any | None = self.commands.get(command_entry.command_name)

            if not executable_command:
                print(f"ERROR >> Command {command_entry.command_name} not found")
                return None
            
            t0: float = time.time()
            res, err = executable_command.execute(
                self.stop_current,
                command_entry.duration,
                command_entry.args,
                command_entry.kwargs,
            )
            logger.debug(f"run_command executed with result = {res} and error = {err}")
            error = None
            if err:
                error = str(err)

            log_entry = CommandExecutionLog(
                command=command_entry.copy(deep=True),
                result=str(res),
                effective_duration=time.time() - t0,
                error=error,
            )
            self._log_exec(log_entry)

        except Exception as e:
            logger.error(f"Error executing {command_entry.command_name}: {str(e)}")
            logger.error(traceback.format_exc())
            log_entry = CommandExecutionLog(
                command=command_entry.copy(deep=True),
                result=None,
                effective_duration=time.time() - t0,
                error=str(e),
            )
            self._add_log(log_entry)

    @synchronized_method
    def execute_now(self, command_name:str, duration:float, interrupt=False, args:list=[], kwargs:dict={}) -> None:
        self.scheduler.append_next(
            CommandEntry(
                command_name=command_name, duration=duration, args=args, kwargs=kwargs
            )
        )
        if interrupt:
            self.stop_current.set()

    @synchronized_method
    def stop(self, interrupt=False) -> None:
        logger.info("Stop request received")

        self.stop_scheduler.set()
        time.sleep(BUSY_WAIT * 5)
        if interrupt:
            self.stop_current.set()
            time.sleep(BUSY_WAIT * 5)
        logger.debug("waiting for scheduler thread to exit")
        if self.schedule_thread is not None and self.schedule_thread.is_alive():
            self.schedule_thread.join(timeout=2)
        logger.info("Scheduler shutdown completed, exiting")

    def get_valid_commands(self) -> dict[str, Callable]:
        # make remote commands list explicit
        return {
            "ls": self.list_commands,
            "get_commands": self.get_commands,
            "get_command": self.get_command,
            "get_command_screenshot": self.get_command_screenshot,
            "list_schedules": self.list_schedules,
            "get_schedule": self.get_schedule,
            "execute_now": self.execute_now,
            "set_schedule": self.set_schedule,
            "save_schedule": self.save_schedule,
            "stop": self.stop,
        }

    def connected(self) -> bool:
        return True


###################################
# Helper to manage as singleton
singleton:CommandExecutor | None = None

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
    parser.add_argument(
        "-c", "--commands", nargs="+", help="list of commands to execute"
    )

    args = parser.parse_args()

    if not args.scheduler:
        # prevent loading of default scheduler file
        executor = CommandExecutor(schedule_file=None)
    else:
        executor = CommandExecutor()

    if args.list:
        print("Listing commands:")
        for command in executor.commands.values():
            print(f"{command.name} - {command.description}")
        # exit(0)

    if args.listen or (is_ipc_enabled() and not args.commands):
        executor.serve()
    else:
        if args.commands:
            for command in args.commands:
                print(f"command = {command}")
                cmds = command.split(":")
                if len(cmds) == 2:
                    executor.execute_now(cmds[0], int(cmds[1]))
                else:
                    executor.execute_now(cmds[0], int(args.duration))
                time.sleep(1)
    executor.stop()
