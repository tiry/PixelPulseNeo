
import time
import json
from datetime import datetime
import socket
import subprocess
import time
import os
import sys
from Matrix.models.encode import json_dumps
from Matrix.driver.base_executor import BUFFER_SIZE

from Matrix.driver.utilz import configure_log, GREEN
import logging
import traceback

logger = logging.getLogger(__name__)
configure_log(logger, GREEN, "Server")

IPC_PORT = 6000

class IPCServer:

    def method_echo(self, *args, **kwargs):
        return "\n".join(["OK", str(args), str(kwargs)])
    
    def get_valid_commands(self):
        return {
            "echo": self.method_echo
        }

    def execute_ipc_request(self, command, args, kwargs):
        response_wrapper = {
            "success" : False,
            "error": None,
            "response" : None
        }

        logger.debug(f" Execute command {command} {args} {kwargs}")

        if command == "ping":
            response_wrapper["response"]= "pong"
            response_wrapper["success"]=True
        else:
            cmds = self.get_valid_commands()
            if command in cmds:
                logger.debug(f"Command :{command} is valid => execute")
                try:
                    result=cmds[command](*args, **kwargs)
                    response_wrapper["success"]=True
                    response_wrapper["response"]= result
                except Exception as e:
                    response_wrapper["error"] = f"exception {e} : {traceback.format_exc()}"
                    logger.error(e)
            else:    
                response_wrapper["error"] = f"Command {command} not found"
                logger.debug(f" return Command Not Found")

        return response_wrapper

    def serve(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', IPC_PORT))
        server_socket.listen(1)

        user = "normal user"
        if os.getuid() == 0:
            user = "root"
        logger.debug(f" IPC Server running as {user} and waiting for commands...")

        while True:
            logger.debug(f" wait for incoming connection request")
            client_socket, addr = server_socket.accept()
            while True:
                json_str = client_socket.recv(1024).decode()
                if len(json_str)==0:
                    time.sleep(0.2)
                    continue
                response_wrapper = {
                    "success" : False,
                    "error": None,
                    "response" : None
                }
                try:
                    logger.debug(f" received message: {json_str}")
                    command, args, kwargs = json.loads(json_str)
                    if command == "disconnect":
                        logger.debug(" closing connection")
                        client_socket.close()
                        break
                    elif command == "exit":
                        logger.debug(" Server shuting down")
                        client_socket.close()
                        sys.exit()              
                    response_wrapper = self.execute_ipc_request(command,args, kwargs)
                    logger.debug(f"Execution response = {response_wrapper}")
                except Exception as e:
                    response_wrapper["success"]=False
                    response_wrapper["error"] = f"Error trying to execute command {command} : {e}"
                    logger.debug(f" while executing command {command} {e}")
                
                json_response = json_dumps(response_wrapper)
                logger.debug(f" Send response {json_response}")
                response_payload = json_response.encode()
                client_socket.send(response_payload)

if __name__ == "__main__":

    logger.debug("Starting IPC server")
    server = IPCServer()
    server.serve()
