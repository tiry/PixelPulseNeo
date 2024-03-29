import json
import argparse
import signal
import os
import sys
import logging
import traceback
from typing import Any
from pydantic import BaseModel
from flask import Flask, jsonify, make_response, request, Response, send_file, send_from_directory
from flask_restx import Api, Resource
from flask_cors import CORS
from Matrix.models.Commands import ScheduleModel
from Matrix.models.resthelper import pydantic_to_restx_model
from Matrix.config import is_ipc_enabled
from Matrix.driver.utilz import configure_log, YELLOW
from Matrix.driver.factory import CommandExecutorSingleton, IPCClientSingleton
from Matrix.driver.ipc.client import IPCClient, IPCClientExecutor
from Matrix.driver.executor import CommandExecutor
from Matrix.driver.monitor import probe
from Matrix.driver.commands.index import TEST_ONLY_COMMANDS
logger: logging.Logger = logging.getLogger(__name__)
configure_log(logger, YELLOW, "API> ")

app = Flask(__name__)  # Creates a Flask application instance with the given name
"""Creates a Flask application instance to host the API endpoints.

The API is defined using OpenAPI 3.0 specification.

The following endpoints are available:

- GET /commands - Returns a list of available commands  
- POST /commands/{name} - Executes the command with the given name
- GET /schedule - Returns the current command schedule
- DELETE /stop - Stops the command executor
"""


executor: IPCClientExecutor | CommandExecutor | None = None


def get_executor() -> IPCClientExecutor | CommandExecutor:
    global executor
    if executor is None:
        if is_ipc_enabled():
            executor = IPCClientSingleton.instance()
            logger.info(f"Returning IPC Client {executor}")
            # logger.info(f"Creating IPC (socket) client root={RUN_AS_ROOT}")
            # executor = IPCClientExecutor(RUN_AS_ROOT, start_server_if_needed=False)
        else:
            executor = CommandExecutorSingleton.instance()
            logger.info(f"Returning inproces client {executor}")
            # executor = instance()
    return executor


def shutdown_cleanly(signum, frame):
    print(f"### Signal handler called with signal  {signum}")
    if executor is not None:
        print("Shuting down Executor")
        executor.stop(interrupt=True)
    # Yeek !
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_cleanly)
signal.signal(signal.SIGINT, shutdown_cleanly)
signal.signal(signal.SIGQUIT, shutdown_cleanly)


# Creates a Flask application instance with the given name
app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

api = Api(
    app,
    version="1.0",
    title="PixelPulseNeoServer",
    description="REST API to interact with PixelPulseNeoServer",
    prefix="/api",
    default="PixelPulseNeoAPI",
    default_label="REST API for PixelPulseNeoServer",
)


@api.route("/commands")
class Commands(Resource):
    def get(self):
        """Returns a JSON array of all available commands.

        Each command is represented as a dictionary with the following fields:

        - `name`: The name of the command
        - `description`: A description of what the command does
        - `screenshots`: Screenshot URLs demonstrating the visual effect of the command
        - `recommended_duration`: recommended duration in s

        """
        logger.info("GET /commands")
        result: list[dict[str, Any]] | None = get_executor().get_commands()
        logger.info(f"result {result}")
        if result is None:
            return jsonify([])
        filtered : list[dict[str, Any]]= []
        
        for cmd in result:
            if cmd["name"] not in TEST_ONLY_COMMANDS:
                filtered.append(cmd)
        logger.info(f"filtered result {filtered}")
        return jsonify(filtered)


@api.route("/schedules")
class Schedules(Resource):
    def get(self):
        """Returns a JSON array of the names of all available schedules / playlists."""
        result: list[str] = get_executor().list_schedules()
        return jsonify(result)


@api.route("/schedules/detailed")
class SchedulesDetailed(Resource):
    def get(self):
        """Returns a JSON array of the names of all available schedules / playlists."""
        names: list[str] = get_executor().list_schedules()
        result = []
        for name in names:
            schedule:ScheduleModel = get_executor().get_schedule(name) # type: ignore
            commands = []
            conditions = []
            try:      
                commands = [ command.command_name for command in schedule.commands]
                conditions = schedule.conditions
            except Exception as e:
                commands = [ command["command_name"] for command in schedule["commands"]] # type: ignore
                conditions = schedule["conditions"] # type:ignore
            resItem = {
                "name" : name,
                "commands" : commands,
                "conditions" : conditions
            }
            result.append(resItem)
        return jsonify(result)
    

@api.route("/screenshots/<command_name>/<screenshot_name>")
class Screenshot(Resource):
    def get(self, command_name, screenshot_name):
        """Returns a screenshot file for the given command and screenshot name.

        Checks that the command and screenshot exist, determines the mimetype
        based on the file extension, and returns the file contents. Returns
        a 404 if the command or screenshot is not found.
        """
        command: dict[str, Any] | None = get_executor().get_command(command_name)
        if command is None:
            return jsonify({"error": "Command not found"}), 404

        screenshot_path: Any | str | None = get_executor().get_command_screenshot(
            command_name, screenshot_name
        )
        if screenshot_path is None:
            return jsonify({"error": "Screenshot not found"}), 404

        _, ext = os.path.splitext(screenshot_name)
        if ext == ".png":
            mimetype = "image/png"
        elif ext == ".gif":
            mimetype = "image/gif"
        else:
            mimetype = "application/octet-stream"

        try:
            if os.path.exists(screenshot_path):
                return send_file(open(screenshot_path, "rb"), mimetype=mimetype)
            else:
                return make_response(jsonify({"error": "Screenshot not found"}), 404)
        except Exception as e:
            logger.error(f"Unable to send screenshot {screenshot_path} - {e}")
            traceback.print_exc()
            return make_response(
                jsonify({"error": f"Unable to resolve screenshot {screenshot_path}"}),
                500,
            )

@api.route("/command", defaults={"command_name": None})
@api.route("/command/<command_name>")
class Command(Resource):
    def get(self, command_name):
        """Returns a JSON dictionnary representing the requested command.

        - `name`: The name of the command
        - `description`: A description of what the command does
        - `screenshots`: Screenshot URLs demonstrating the visual effect of the command
        - `recommended_duration`: recommended duration in s

        """
        logger.info(f"GET /command/{command_name}")
        
        if command_name is None:
            return jsonify(get_executor().get_current_command())
        
        result: dict[str, Any] | None = get_executor().get_command(command_name)
        logger.info(f"result {result}")
        if result is None:
            return jsonify([])
        return jsonify(result)
   
    @api.doc(
        params={
            "duration": {
                "description": "Duration of the command",
                "type": "integer",
                "required": False,
            },
            "interrupt": {
                "description": "Interrup ongoing command",
                "type": "boolean",
                "required": False,
                "default": False,
            },
        }
    ) 
    def post(self, command_name):
        """Executes the command with the given name.

        Returns a JSON dictionary with the following fields:

        - `result`: A message indicating the result of the command execution
        """
        if command_name is None:
            return make_response(jsonify({"error": "no command name was provided"}), 400)
            
        # Access the duration query parameter with a default value if it's not provided
        duration: float = request.args.get("duration", default=10, type=float)
        interrupt: str | bool = request.args.get("interupt", default="false", type=bool)

        try:
            # result is async and only accessible via audit log
            get_executor().execute_now(command_name, duration, interrupt=interrupt)  # type: ignore
            return jsonify({"message": f"Command '{command_name}' executed"})
        except Exception as e:
            print(f"Error during command execution for {command_name}")
            print(e)
            return make_response(jsonify({"error": str(e)}), 500)


@api.route("/message/<command_name>")
class MsgCommand(Resource):
    @api.doc(
        params={
            "message": {
                "description": "Message content",
                "type": "string",
                "required": True,
            },
        }
    )
    def post(self, command_name):
        """Sends a messsage to the command with the given name.

        - `result`: 
        """

        # Access the duration query parameter with a default value if it's not provided
        message: str| None = request.args.get("message", type=str)
        if message is None:
            message:  str | None = request.get_data() # type:ignore 
        
        if type(message) == bytes:
            message = message.decode("utf-8")
                    
        logger.info(f"received Posted message for {command_name} with payload {message}")

        try:
            # result is async and only accessible via audit log
            get_executor().send_command_message(command_name, message)  # type: ignore
            return jsonify({"message": f"Message '{message}' sent to '{command_name}'"})
        except Exception as e:
            print(f"Error during command execution for {command_name}")
            print(e)
            return make_response(jsonify({"error": str(e)}), 500)


rest_schedule = pydantic_to_restx_model(api, ScheduleModel)  # type: ignore

@api.route("/schedule/<playlist_name>/execute")
class ScheduleExec(Resource):
    def post(self, playlist_name):
        """Play the selected playlist
        - `result`: None
        """
        get_executor().play_schedule(playlist_name)
        return make_response("OK", 200)

@api.route("/schedule", defaults={"playlist_name": None})
@api.route("/schedule/<playlist_name>")
class Schedule(Resource):
    def get(self, playlist_name: str | None = None):
        """Returns the executor's current schedule.

        The schedule is returned as a JSON array containing dictionaries
        with the following fields:

        - `name`: The name of the scheduled command
        - `interval`: The interval in seconds between runs of this command
        """
        schedule: ScheduleModel | None = get_executor().get_schedule(playlist_name)
        if not schedule:
            return make_response(
                jsonify({"error": f"Schedule '{playlist_name}' not found"}), 404
            )

        print(f"SCHEDULE = {schedule}")
        if issubclass(schedule.__class__, BaseModel):
            return json.loads(schedule.model_dump_json())
        else:
            return schedule

    @api.expect(rest_schedule)
    def post(self, playlist_name=None):
        """Updates the executor's schedule.

        Accepts a JSON array containing the new schedule and replaces the
        executor's current schedule with it. Validates that the named commands
        exist before updating the schedule.
        """
        payload: dict[str, Any] | None = request.json

        if not payload:
            print("payload is None")
            return make_response(jsonify({"error": "No Payload"}), 500)

        print(f"payload type {type(payload)} content: {payload}")

        # convert back to SchedulModel // Sanitize
        schedule = ScheduleModel(**payload)

        print(f"converted schedule {schedule}")

        # validate commands
        for item in schedule.commands:
            command_name = item.command_name
            if get_executor().get_command(command_name) is None:
                return make_response(
                    jsonify({"error": f"Command '{command_name}' not found"}), 404
                )

        # update schedule
        get_executor().set_schedule(schedule, playlist_name)

        # flush / persist on disk
        if playlist_name:
            get_executor().save_schedule()

        return jsonify({"result": "Schedule updated"})

@api.route("/status")
@api.route("/metrics/api")
class Status(Resource):
    def get(self):
            """Returns Metrics 
            """
            
            metrics: dict[str, Any] = probe.all_metrics()
            return jsonify(metrics)
        
@api.route("/metrics/all")
@api.route("/metrics/driver")
class DriverMetrics(Resource):
    def get(self):
            """Returns Metrics 
            """
            metrics: dict[str, Any]|None = get_executor().get_metrics()
            return jsonify(metrics)
        
        
@api.route("/power/sleep")
class Sleep(Resource):
    def get(self):
        """Activate the Sleep mode.

        """
        exe = get_executor()
        if exe is not None:
            logger.info("putting the executor to sleep")
            try:
                exe.sleep()
                logger.info("sleep command executed")
                return jsonify({"result": "Sleep mode activated"})
            except Exception as e:
                print(f"Error during sleep command")
                print(e)
                return make_response(jsonify({"error": str(e)}), 500)
        else:
            return make_response(jsonify({"error": f"No Executor found"}), 500)
            
@api.route("/power/wakeup")
class Wakeup(Resource):
    def get(self):
        """Wakeup from the Sleep mode.

        """
        exe = get_executor()
        if exe is not None:
            logger.info("Waking up the executor to sleep")
            try:
                exe.wakeup()
                return jsonify({"result": "Sleep mode de-activated"})
            except Exception as e:
                print(f"Error during wakup")
                print(e)
                return make_response(jsonify({"error": str(e)}), 500)
        else:
            return make_response(jsonify({"error": f"No Executor found"}), 500)

@api.route("/power/shutdown")
class Shutdown(Resource):
    def get(self):
        global executor
        if executor is not None:
            logger.info("API Server shutting down Executor")
            executor.stop(interrupt=True)
            if issubclass(executor.__class__, IPCClient):
                executor.disconnect()  # type: ignore
                # executor.kill_server()
            executor = None
            logger.info("API Server: executor shutdown completed")
        # time.sleep(1)
        # func = request.environ.get('werkzeug.server.shutdown')
        # if func is not None:
        #    print("werkzeug shut down")
        #    func()
        #    print("werkzeug shut down completed")
        # os.kill(os.getpid(), signal.SIGINT)
        logger.info("Bye !")
        return "server exit"


@app.route("/web/")
@app.route("/web/<path:path>")
def serve_webapp(path=None):
    if path is None or path == "":
        path = "index.html"
    print(f"serve_webapp for path {path}")
    try:
        response: Response =  send_from_directory("../../pixel-pulse-neo-client/build/", path)
        return response
    except Exception as e:
        print(f"Error during serve_webapp for path {path}")
        print(f"Intercept 404 for path {path}")
        if path in ["status", "schedule", "commands", "playlists"]:
            return make_response({}, 304)
        else:
            return make_response(jsonify({"error": str(e)}), 500)


def bool_to_on_off(bvalue:bool):
    return "on" if bvalue else "off"

@api.route("/watchdog")
class WatchDogGet(Resource):
    def get(self, expected_state: bool | None = None):
        """Returns the watchdog state
        
        """
        return bool_to_on_off(get_executor().watchdog())
    
@api.route("/watchdog/<expected_state>")
class WatchDogSet(Resource):
    
    def post(self, expected_state: str):
        
        bool_state: bool = expected_state.lower()=='on'
        print(f"set watchdog state to {bool_state}")
        return bool_to_on_off(get_executor().watchdog(bool_state))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="enable flash debug mode", action="store_true")
    parser.add_argument("--noreload", help="disable reloader", action="store_true")

    args = parser.parse_args()

    debug = args.debug
    reload = debug
    if args.noreload:
        reload = False

    print(f"start API server with debug={debug} and use_reloader={reload}")
    app.run(debug=debug, use_reloader=reload, host="0.0.0.0")
