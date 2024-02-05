from flask import Flask, jsonify, make_response, request, send_file
from flask_restx import Api, Resource
from flask_cors import CORS
import json
import argparse
from Matrix.driver.executor import instance
import signal, os, sys
from Matrix.models.Commands import ScheduleModel
from Matrix.models.resthelper import pydantic_to_restx_model

from flask_restx import fields

app = Flask(__name__)# Creates a Flask application instance with the given name
"""Creates a Flask application instance to host the API endpoints.

The API is defined using OpenAPI 3.0 specification.

The following endpoints are available:

- GET /commands - Returns a list of available commands  
- POST /commands/{name} - Executes the command with the given name
- GET /schedule - Returns the current command schedule
- DELETE /stop - Stops the command executor
"""


# in debug + reload mode, there will be 2 python interpreter and then 2 singletons ...
#if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  
executor = instance()

def shutdown_cleanly(signum, frame):
    print(f"### Signal handler called with signal  {signum}")

    if (executor):
        print("Shuting down Executor")
        executor.stop(interrupt=True)

    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_cleanly)
signal.signal(signal.SIGINT, shutdown_cleanly)
signal.signal(signal.SIGQUIT, shutdown_cleanly)


# Creates a Flask application instance with the given name
app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

# doc='/api/docs'
api = Api(app, version='1.0', title='PixelPulseNeoServer', description='REST API to interact with PixelPulseNeoServer')

@api.route('/commands')
class Commands(Resource):

    def get(self):
        """Returns a JSON array of all available commands.

        Each command is represented as a dictionary with the following fields:

        - `name`: The name of the command
        - `description`: A description of what the command does  
        - `screenshots`: Screenshot URLs demonstrating the visual effect of the command
        """
        result = executor.get_commands()
        return jsonify(result)

@api.route('/schedules')
class Schedules(Resource):

    def get(self):
        """Returns a JSON array of the names of all available schedules / playlists.
        """
        result = executor.list_schedules()
        return jsonify(result)

@api.route('/screenshots/<command_name>/<screenshot_name>')
class Screenshot(Resource):

    def get(self,command_name, screenshot_name):
        """Returns a screenshot file for the given command and screenshot name.

        Checks that the command and screenshot exist, determines the mimetype
        based on the file extension, and returns the file contents. Returns
        a 404 if the command or screenshot is not found.
        """
        command = executor.get_command(command_name)
        if command is None:
            return jsonify({"error": "Command not found"}), 404
        
        screenshot_path = executor.get_command_screenshot(command_name, screenshot_name)
        if screenshot_path is None:
            return jsonify({"error": "Screenshot not found"}), 404

        _, ext = os.path.splitext(screenshot_name)
        if ext == '.png':
            mimetype = 'image/png'
        elif ext == '.gif':
            mimetype = 'image/gif'
        else:
            mimetype = 'application/octet-stream'
        
        if os.path.exists(screenshot_path):
            return send_file(open(screenshot_path, "rb"), mimetype=mimetype)
        else:
            return make_response(jsonify({"error": "Screenshot not found"}), 404)

@api.route('/command/<command_name>')
class Command(Resource):

    @api.doc(params={
        'duration': {'description': 'Duration of the command', 'type': 'integer', 'required': False},
        'interrupt': {'description': 'Interrup ongoing command', 'type': 'boolean', 'required': False, 'default' : False}
        })
    def post(self, command_name):
        """Executes the command with the given name.

        Returns a JSON dictionary with the following fields:

        - `result`: A message indicating the result of the command execution
        """
        print("XXX Execute")
        # Access the duration query parameter with a default value if it's not provided
        duration = request.args.get('duration', default=10, type=int)
        interrupt = request.args.get('interupt', default="false", type=bool)
        
        try:
            executor.execute_now(command_name, duration, interrupt=interrupt)
            return jsonify({"result": f"Command '{command_name}' executed"})
        except Exception as e:
            print(f"Error during command execution for {command_name}")
            print(e)      
            return make_response(jsonify({"error": str(e)}), 500)


rest_schedule = pydantic_to_restx_model(api, ScheduleModel)

@api.route('/schedule', defaults={'playlist_name': None})
@api.route('/schedule/<playlist_name>')
class Schedule(Resource):

    def get(self, playlist_name=None):
        """Returns the executor's current schedule.

        The schedule is returned as a JSON array containing dictionaries 
        with the following fields:

        - `name`: The name of the scheduled command  
        - `interval`: The interval in seconds between runs of this command
        """
        schedule = executor.get_schedule(playlist_name)
        if not schedule:
            return make_response(jsonify({"error": f"Schedule '{playlist_name}' not found"}), 404)
        
        print(f"SCHEDULE = {schedule}")
        return json.loads(schedule.model_dump_json())  

    @api.expect(rest_schedule)
    def post(self, playlist_name=None):
        """Updates the executor's schedule.

        Accepts a JSON array containing the new schedule and replaces the 
        executor's current schedule with it. Validates that the named commands
        exist before updating the schedule.
        """
        payload = request.json

        print(f"payload type {type(payload)} content: {payload}")
        
        # convert back to SchedulModel // Sanitize
        schedule = ScheduleModel(**payload) 

        print(f"converted schedule {schedule}")

        # validate commands 
        for item in schedule.commands:
            command_name = item.command_name
            if executor.get_command(command_name) is None:
                return make_response(jsonify({"error": f"Command '{command_name}' not found"}), 404)

        # update schedule
        executor.set_schedule(schedule, playlist_name)

        # flush / persist on disk
        if playlist_name:
            executor.save_schedule()

        return jsonify({"result": "Schedule updated"})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="enable flash debug mode", action="store_true")
    parser.add_argument("--noreload", help="disable reloader", action="store_true")
     
    args = parser.parse_args()
    
    debug = args.debug
    reload = debug
    if args.noreload:
        reload = False

    app.run(debug=debug, use_reloader=reload)
