from flask import Flask, jsonify, make_response, request, send_file
from flask_restx import Api, Resource
from flask_cors import CORS
import json
import argparse
from Matrix.driver.executor import instance
import signal, os, sys
from Matrix.models.Commands import Schedule, CommandEntry
from Matrix.models.resthelper import pydantic_to_restx_model

from flask_restx import fields


# Creates a Flask application instance with the given name
app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

# doc='/api/docs'
api = Api(app, version='1.0', title='PixelPulseNeoServer', description='REST API to interact with PixelPulseNeoServer')


rest_schedule = pydantic_to_restx_model(api, Schedule)

#rest_command = pydantic_to_restx_model(api, CommandEntry)

print(rest_schedule)

#schedule_model = api.model('Schedule', {
#    'schedule': fields.List(rest_command)
#})


#from flask_restx import fields

# Define the model for the schedule item
#schedule_item = api.model('ScheduleItem', {
#    'command_name': fields.String(required=True, description='The name of the command'),
#    'interval': fields.Integer(required=True, description='The interval in seconds between runs of this command')
#})

## Define the model for the schedule (an array of schedule items)
#schedule_model = api.model('Schedule', {
#    'schedule': fields.List(fields.Nested(schedule_item), required=True, description='The list of schedule items')
#})

