import time
import json
import socket
import os
import sys
import logging
import traceback
import threading
from typing import Any, Callable
from Matrix.models.encode import json_dumps
from Matrix.driver.base_executor import synchronized_method
from Matrix.driver.utilz import configure_log, GREEN

logger: logging.Logger = logging.getLogger(__name__)
configure_log(logger, GREEN, "Server")

IPC_PORT = 6000

class IPCServer:
    def method_echo(self, *args, **kwargs) -> str:
        return "\n".join(["OK", str(args), str(kwargs)])

    def get_valid_commands(self) -> dict[str, Callable]:
        return {"echo": self.method_echo}

    @synchronized_method
    def execute_ipc_request(
        self, command: str, args: list, kwargs: dict
    ) -> dict[str, Any]:
        response_wrapper: dict[str, Any] = {
            "success": False,
            "error": None,
            "response": None,
        }

        # Yeark
        if len(args) > 0:
            if type(args[-1]) == dict and len(kwargs) == 0: # type: ignore
                kwargs = args.pop()
                if type(args[-1]) == list and len(args[-1]) == 0:
                    args.pop()

        logger.debug(f" Execute command {command} {args} {kwargs}")

        if command == "ping":
            response_wrapper["response"] = "pong"
            response_wrapper["success"] = True
        else:
            cmds: dict[str, Callable] = self.get_valid_commands()
            if command in cmds:
                logger.debug(f"Command :{command} is valid => execute")
                try:
                    result = cmds[command](*args, **kwargs)
                    response_wrapper["success"] = True
                    response_wrapper["response"] = result
                except Exception as e:
                    response_wrapper[
                        "error"
                    ] = f"exception {e} : {traceback.format_exc()}"
                    logger.error(e)
            else:
                response_wrapper["error"] = f"Command {command} not found"
                logger.debug(" return Command Not Found")

        return response_wrapper

    def handle_client(self, client_socket, addr) -> None:
        connected = True
        response_wrapper: dict[str, Any] = {}
        while connected:
            json_str: str = client_socket.recv(1024).decode()
            if len(json_str) == 0:
                time.sleep(0.2)
                continue
            response_wrapper = {"success": False, "error": None, "response": None}
            try:
                logger.debug(f" received message: {json_str}")
                command, args, kwargs = json.loads(json_str)
                if command == "disconnect":
                    logger.debug(" closing connection")
                    client_socket.close()
                    connected = False
                    break
                elif command == "exit":
                    logger.debug(" Server shuting down")
                    self.shutdown_requested = True
                    self.server_socket.shutdown(socket.SHUT_RD)
                    client_socket.close()
                    sys.exit()
                response_wrapper = self.execute_ipc_request(command, args, kwargs)
                logger.debug(f"Execution response = {response_wrapper}")
            except Exception as e:
                response_wrapper["success"] = False
                response_wrapper[
                    "error"
                ] = f"Error trying to execute command {command} : {e}"
                logger.debug(f" while executing command {command} {e}")

            json_response: str = json_dumps(response_wrapper)
            logger.debug(f" Send response {json_response}")
            response_payload: bytes = json_response.encode()
            client_socket.send(response_payload)

    def serve(self):
        # XXX switch to AF_UNIX
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("localhost", IPC_PORT))
        server_socket.listen(1)

        user = "normal user"
        if os.getuid() == 0:
            user = "root"
        logger.debug(f" IPC Server running as {user} and waiting for commands...")

        client_id = 0

        self.server_socket = server_socket
        self.shutdown_requested = False

        while not self.shutdown_requested:
            logger.debug(" wait for incomming connection request")
            client_socket, addr = server_socket.accept()
            client_id += 1
            thread = threading.Thread(
                target=self.handle_client, args=(client_socket, addr)
            )
            thread.start()
            print(f"client {client_id} handled by thread {thread}")
            time.sleep(0.1)


if __name__ == "__main__":
    logger.debug("Starting IPC server")
    server = IPCServer()
    server.serve()
