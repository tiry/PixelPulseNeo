
import time
import json
from datetime import datetime
import socket
import subprocess
import time

from base_executor import BaseCommandExecutor, BUFFER_SIZE

class IPCClientExecutor(BaseCommandExecutor):

    def __init__(self):
        
        self.start_process()
        self.connect()

    def start_process(self):

        # Start as root using subprocess
        subprocess.Popen(['sudo', 'python3', 'executor.py -s'])
        time.sleep(1)  # Wait for the server to start

    def connect(self):
        # connect 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 6000))
        self.client = client_socket

    def disconnect(self):
        if self.client:
            self.client.close()

    def send_command(self,command, args, kwargs):

        p = [command,args, kwargs]
        json_call = json.dumps(p)
        self.client.send(json_call.encode())
        response = self.client.recv(BUFFER_SIZE).decode()
        json_response = json.loads(response)

        return json_response


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

class IPCServer:

    def execute_ipc_request(self, command, args, kwargs):
        response_wrapper = {
            "success" : False,
            "error": None,
            "response" : None
        }

        response_wrapper["error"] = f"Command {command} not found"
        return response_wrapper

    def serve(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 6000))
        server_socket.listen(1)

        user = "normal user"
        if os.getuid() == 0:
            user = "root"
        print(f"IPC Server running as {user} and waiting for commands...")

        while True:
            client_socket, addr = server_socket.accept()
            while True:
                json_str = client_socket.recv(BUFFER_SIZE).decode()
                command, args, kwargs = json.loads(json_str)
                response_wrapper = {
                    "success" : False,
                    "error": None,
                    "response" : None
                }
                try:
                    if command == "exit":
                        print("Server shuting down")
                        client_socket.close()
                        self.stop()
                        break
                    return self.execute_ipc_request(command,args, kwargs)
                except Exception as e:
                    response_wrapper["success"]=False
                    response_wrapper["error"] = str(e)
                    print(e)
                
                json_response = json.dumps(response_wrapper)
                client_socket.send(json_response.encode())
