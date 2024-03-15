import time
import json
import socket
from typing import Any
import subprocess
import sys
import traceback
from pathlib import Path
import argparse
import logging
import signal

from Matrix.driver.base_executor import BaseCommandExecutor, BUFFER_SIZE
from Matrix.driver.ipc.server import IPC_PORT
from Matrix.models.Commands import ScheduleModel
from Matrix.driver.utilz import configure_log, BLUE
from Matrix.models.encode import json_dumps
from Matrix.driver.base_executor import synchronized_method

logger: logging.Logger = logging.getLogger(__name__)
configure_log(logger, BLUE, "Client")


class IPCClient:
    def __init__(self, start_server_if_needed: bool = True) -> None:
        self.server_process: subprocess.Popen | None = None
        self.client: socket.socket | None = None
        try:
            self.connect()
        except ConnectionRefusedError as e:
            logger.info(f"Unable to connect to server {e}")
            traceback.print_exc()
            if start_server_if_needed:
                logger.debug("start_server_if_needed=True => starting server")
                self.start_server_process()
                self.connect()
            else:
                logger.info(
                    "start_server_if_needed=False => we can not continue, exiting"
                )

    def get_shell_command(self) -> str:
        return "python -m Matrix.driver.ipc.server"

    def start_server_process(self) -> None:
        current_dir: Path = Path(__file__).parent
        # Get the root
        root_dir: Path = current_dir.parent.parent

        cmd: str = self.get_shell_command()
        cmd_line: str = f'export PYTHONPATH="{root_dir}/"; {cmd}'

        logger.debug(f"shell command = {cmd_line}")

        self.server_process = subprocess.Popen(cmd_line, shell=True)
        time.sleep(1)  # Wait for the server to start

    def connect(self) -> None:
        # connect
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", IPC_PORT))
        self.client = client_socket
        logger.debug(f"Connected via socket {client_socket}")

    def disconnect(self) -> None:
        if self.client:
            logger.debug("Disconnect from server")
            self.send_command("disconnect")
            self.client.close()

    def send_command(self, command: str, *args, **kwargs) -> Any:
        p = [command, args, kwargs]
        json_call: str = json_dumps(p)

        if not self.client:
            print(f"No client socket to send command {command}")
            return None

        logger.debug(f"Send command call : {json_call}")
        self.client.send(json_call.encode())
        response: str | None = None
        response = self.client.recv(BUFFER_SIZE).decode()

        logger.debug(f"received response : {response}")
        if len(response) > 0:
            json_response = json.loads(response)
        else:
            return {
                "success": command == "exit",
                "error": "Connection Closed by server",
                "response": None,
            }

        return json_response

    def shutdown_server(self) -> None:
        logger.debug("Send Exit command to server and disconnecting")
        self.send_command("exit")
        if self.client:
            self.client.close()

    def kill_server(self):
        self.disconnect()
        if self.server_process:
            self.server_process.kill()


class IPCClientExecutor(IPCClient, BaseCommandExecutor):
    def __init__(self, run_as_root: bool = False, start_server_if_needed: bool = True):
        self.run_as_root: bool = run_as_root
        IPCClient.__init__(self, start_server_if_needed=start_server_if_needed)
        BaseCommandExecutor.__init__(self)

    def get_shell_command(self) -> str:
        prefix: str = ""
        if self.run_as_root:
            prefix = "sudo "

        return f"{prefix}python -m Matrix.driver.executor --scheduler --listen"

    @synchronized_method
    def send_command(self, command, *args, **kwargs) -> Any | None:
        json_response: Any = IPCClient.send_command(self, command, *args, **kwargs)
        response: Any = json_response["response"]
        if response:
            return response
        else:
            return None

    @synchronized_method
    def list_commands(self) -> list[str]:
        return self.send_command("ls")  # type: ignore

    @synchronized_method
    def get_commands(self) -> list[dict[str, Any]] | None:
        return self.send_command("get_commands")

    @synchronized_method
    def get_command(self, name) -> dict[str, Any] | None:
        return self.send_command("get_command", name)

    @synchronized_method
    def get_command_screenshot(self, name, screenshot_name) -> Any | None:
        return self.send_command("get_command_screenshot", name, screenshot_name)

    @synchronized_method
    def list_schedules(self) -> list[str]:
        return self.send_command("list_schedules")  # type:ignore

    @synchronized_method
    def get_schedule(self, playlist_name: str | None) -> ScheduleModel | None:
        return self.send_command("get_schedule", playlist_name)

    @synchronized_method
    def set_schedule(
        self, schedule: ScheduleModel, playlist_name: str | None
    ) -> Any | None:
        return self.send_command("set_schedule", schedule, playlist_name)

    @synchronized_method
    def play_schedule(self, playlist_name: str | None) -> None:
        return self.send_command("play_schedule", playlist_name)
   
    @synchronized_method
    def execute_now(
        self,
        command_name: str,
        duration: float,
        interrupt=False,
        args: list = [],
        kwargs: dict = {},
    ) -> Any | None:
        kwargs["interrupt"] = interrupt
        kwargs["duration"] = duration
        return self.send_command("execute_now", command_name, args, kwargs)

    @synchronized_method
    def save_schedule(self) -> Any | None:
        return self.send_command("save_schedule")

    @synchronized_method
    def stop(self, interrupt=False) -> Any | None:
        res: Any | None = self.send_command("stop", interrupt=interrupt)
        return res

    def connected(self) -> bool:
        if self.client is None:
            return False
        else:
            # XXX Ping Server
            return True

    @synchronized_method
    def sleep(self) -> None:
        """
        Put the executor to sleep
        """
        self.send_command("sleep")

    @synchronized_method
    def wakeup(self) -> None:
        self.send_command("wakeup")
 
    @synchronized_method
    def get_current_command(self) -> str | None:
        return self.send_command("get_current_command")  # type:ignore

    @synchronized_method
    def send_command_message(self, command_name:str, message:str) -> str | None:
        return self.send_command("send_command_message", command_name, message)  # type:ignore
 
    @synchronized_method
    def get_metrics(self) -> dict[str, Any] | None:
        return self.send_command("get_metrics")  # type:ignore
 
    @synchronized_method
    def watchdog(self, expected_state:bool | None = None) -> bool:
        if expected_state is None:
            return self.send_command("watchdog")  # type:ignore
        else:
            return self.send_command("watchdog", expected_state)  # type:ignore

class InteractiveRemoteCLI:
    def __init__(self) -> None:
        self.client = IPCClientExecutor(start_server_if_needed=False)
        signal.signal(signal.SIGTERM, self.shutdown_cleanly)
        signal.signal(signal.SIGINT, self.shutdown_cleanly)
        signal.signal(signal.SIGQUIT, self.shutdown_cleanly)

    def run(self) -> None:
        try:
            while True:
                cmd = input("remote cmd executor>")  # Python 3
                # print(cmd)
                res = None
                cmds: list[str] = cmd.split(" ")
                cmd: str = cmds[0]
                args: list[str] = cmds[1:]
                if cmd == "exit":
                    self.client.disconnect()
                    break
                elif cmd == "ls":
                    if len(args) == 0:
                        print("missing argument:")
                        print("  ls commands to list available commands")
                        print("  ls schedules to list available schedules / playlists")
                        continue
                    else:
                        if args[0] == "commands":
                            res: Any | None = self.client.list_commands()
                        elif args[0] == "schedules":
                            res = self.client.list_schedules()
                        else:
                            print(f"Unknown target {args[0]}")
                            continue
                elif cmd == "commands":
                    res = self.client.get_commands()
                elif cmd == "command":
                    res = self.client.get_command(args[0])
                elif cmd == "screenshot":
                    res = self.client.get_command_screenshot(args[0], args[1])
                elif cmd == "schedule":
                    res = self.client.get_schedule(args[0])
                elif cmd == "run":
                    if len(args) == 0:
                        print(
                            "missing argument: run <command_name> <duration(=10)> <interrupt(=False)>"
                        )
                        continue
                    cmd_name: str = args[0]
                    duration = 10
                    interrupt = False
                    if len(args) > 1:
                        duration = int(args[1])
                    if len(args) > 2:
                        interrupt: bool = args[2].lower() == "true"
                    res = self.client.execute_now(cmd_name, duration, interrupt)
                elif cmd == "set_schedule":
                    if len(args) < 2:
                        print("missing argument: set_schedule <schedule_name> <json>")
                        continue
                    schedule_name: str = args[0]
                    data: str = " ".join(args[1:])
                    data = data.replace("'", '"')
                    json_data = json.loads(data)
                    schedule = ScheduleModel(**json_data)
                    res = self.client.set_schedule(schedule, schedule_name)
                elif cmd == "save_schedule":
                    res = self.client.save_schedule()
                else:
                    print(f"Command {cmd} not supportted by client")
                    continue

                if isinstance(res, dict) and "error" in res and len(res["error"]) > 0:
                    print(f'Server returned an Error : {res["error"]}')
                else:
                    if isinstance(res, list):
                        for item in res:
                            print(item)
                    else:
                        print(res)
                    print("")
        except Exception as e:
            print(f"error trying to execute {e}")
            print(traceback.format_exc())
            self.client.disconnect()

    def shutdown_cleanly(self, signum, frame):
        print(f"### Signal handler called with signal  {signum}")
        self.client.disconnect()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--remotecli", help="Use remote CLI mode", action="store_true")

    args = parser.parse_args()

    remotecli = args.remotecli

    if remotecli:
        rcli = InteractiveRemoteCLI()
        rcli.run()
        print("remote CLI exited")

    else:
        logger.debug("Starting IPC client")

        # clean connection / disconnection use case
        client = IPCClient()

        client.send_command("dummy", 1, 2, 3, foo="bar")
        client.send_command("dummy2", 1, foo="beer")

        client.disconnect()

        # connect then kill server
        client = IPCClient()

        client.send_command("dummy3", 1, oho="nino")
        client.send_command("exit")
