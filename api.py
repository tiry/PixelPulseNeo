from flask import Flask, jsonify, request, send_file
from flask_restx import Api, Resource
from flask_cors import CORS

from executor import CommandExecutor
import os

app = Flask(__name__)# Creates a Flask application instance with the given name
"""Creates a Flask application instance to host the API endpoints.

The API is defined using OpenAPI 3.0 specification.

The following endpoints are available:

- GET /commands - Returns a list of available commands  
- POST /commands/{name} - Executes the command with the given name
- GET /schedule - Returns the current command schedule
- DELETE /stop - Stops the command executor
"""


# Creates a Flask application instance with the given name

executor = CommandExecutor(scheduler_enabled=False)


app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

api = Api(app, version='1.0', title='PixelPulseNeoServer', description='REST API to interact with PixelPulseNeoServer')
# doc='/api/docs'

@api.route('/commands')
class Commands(Resource):

    def get(self):
        """Returns a JSON array of all available commands.

        Each command is represented as a dictionary with the following fields:

        - `name`: The name of the command
        - `description`: A description of what the command does  
        - `screenshots`: Screenshot URLs demonstrating the visual effect of the command
        """
        commands = executor.get_commands()
        result = []
        for name in commands:
            cmd = commands[name]
            result.append({
                "name": cmd.name,
                "description": cmd.description,
                "screenshots": cmd.getScreenShots()
            })
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
        
        screenshot = command.getScreenShot(screenshot_name)
        if screenshot is None:
            return jsonify({"error": "Screenshot not found"}), 404

        _, ext = os.path.splitext(screenshot_name)
        if ext == '.png':
            mimetype = 'image/png'
        elif ext == '.gif':
            mimetype = 'image/gif'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(screenshot, mimetype=mimetype)

@api.route('/command/<name>')
class Command(Resource):

    def post(self, name):
        """Executes the command with the given name.

        Returns a JSON dictionary with the following fields:

        - `result`: A message indicating the result of the command execution
        """
        try:
            executor.execute_now(name)
            return jsonify({"result": f"Command '{name}' executed"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@api.route('/schedule')
class Schedule(Resource):

    def get(self):
        """Returns the executor's current schedule.

        The schedule is returned as a JSON array containing dictionaries 
        with the following fields:

        - `name`: The name of the scheduled command  
        - `interval`: The interval in seconds between runs of this command
        """

        if len(executor.schedule)==0:
            executor.load_schedule()

        return jsonify(executor.schedule)

    def post(self):
        """Updates the executor's schedule.

        Accepts a JSON array containing the new schedule and replaces the 
        executor's current schedule with it. Validates that the named commands
        exist before updating the schedule.
        """
        new_schedule = request.json
        print(new_schedule)
        for item in new_schedule:
            command_name = item['command_name']
            if executor.get_command(command_name) is None:
                return jsonify({"error": f"Command '{command_name}' not found"}), 400
        
        executor.schedule = new_schedule
        executor.save_schedule()
        return jsonify({"result": "Schedule updated"})


if __name__ == '__main__':
    app.run(debug=True)
