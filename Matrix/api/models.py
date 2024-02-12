from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from Matrix.models.Commands import Schedule
from Matrix.models.resthelper import pydantic_to_restx_model


# Creates a Flask application instance with the given name
app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

# doc='/api/docs'
api = Api(
    app,
    version="1.0",
    title="PixelPulseNeoServer",
    description="REST API to interact with PixelPulseNeoServer",
)


rest_schedule = pydantic_to_restx_model(api, Schedule)

# rest_command = pydantic_to_restx_model(api, CommandEntry)

print(rest_schedule)

# schedule_model = api.model('Schedule', {
#    'schedule': fields.List(rest_command)
# })


# from flask_restx import fields

# Define the model for the schedule item
# schedule_item = api.model('ScheduleItem', {
#    'command_name': fields.String(required=True, description='The name of the command'),
#    'interval': fields.Integer(required=True, description='The interval in seconds between runs of this command')
# })

## Define the model for the schedule (an array of schedule items)
# schedule_model = api.model('Schedule', {
#    'schedule': fields.List(fields.Nested(schedule_item), required=True, description='The list of schedule items')
# })
