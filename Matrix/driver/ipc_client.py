import time
import json
from datetime import datetime
import socket
import subprocess
from time import sleep
import os
import sys
from pathlib import Path

from Matrix.driver.base_executor import BaseCommandExecutor, BUFFER_SIZE
from Matrix.driver.ipc_server import IPC_PORT

from Matrix.driver.utilz import configure_log, BLUE
import logging

logger = logging.getLogger(__name__)
configure_log(logger, BLUE, "Client")

class IPCClient():

    def __init__(self):
        
        self.server_process=None
        try:
            self.connect()
        except ConnectionRefusedError as e:
            logger.debug("Unable to connect to server")
            logger.debug("=> starting server")  
            self.start_server_process()
            self.connect()

            
    def get_shell_command(self):

        return "python -m Matrix.driver.ipc_server"

    def start_server_process(self):
        
        current_dir = Path(__file__).parent
        # Get the root
        root_dir = current_dir.parent.parent

        cmd = self.get_shell_command()
        cmd_line = f'export PYTHONPATH="{root_dir}/"; {cmd}'

        logger.debug(f"shell command = {cmd_line}")

        self.server_process = subprocess.Popen(cmd_line, shell=True)
        time.sleep(1)  # Wait for the server to start

    def connect(self):
        # connect
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', IPC_PORT))
        self.client = client_socket
        logger.debug(f"Connected via socket {client_socket}")

    def disconnect(self):
        if self.client:
            logger.debug("Disconnect from server")
            self.send_command("disconnect")
            self.client.close()

    def send_command(self,command, *args, **kwargs):

        p = [command,args, kwargs]
        json_call = json.dumps(p)

        logger.debug(f"Send command call : {json_call}")
        self.client.send(json_call.encode())
        response=None
        response = self.client.recv(BUFFER_SIZE).decode()
        
        logger.debug(f"received response : {response}")
        if len(response)>0:
            json_response = json.loads(response)
        else:
            return {
                    "success" : command == "exit",
                    "error": "Connection Closed by server",
                    "response" : None
            }

        return json_response
    
    def kill_server(self):
        self.disconnect()
        if (self.server_process):
            self.server_process.kill()


class IPCClientExecutor(IPCClient, BaseCommandExecutor):

    def __init__(self):

        IPCClient.__init__(self)
        BaseCommandExecutor.__init__(self)

    def get_shell_command(self):
        return "sudo python -m Matrix.driver.ipc_server"
    
    def list_commands(self):

        pass
    
    def get_commands(self):
        pass
    
    def get_command(self, name):
        pass

    def load_schedule(self, schedule_file=None):
        pass

    def run_command(self, command):
        pass

    def run_schedule(self):
        pass


if __name__ == "__main__":

    logger.debug("Starting IPC client")

    # clean connection / disconnection use case
    client = IPCClient()

    client.send_command("dummy", 1,2,3, foo ="bar")
    client.send_command("dummy2", 1, foo ="beer")

    client.disconnect()

    # connect then kill server
    client = IPCClient()

    client.send_command("dummy3", 1, oho ="nino")
    client.send_command("exit")

