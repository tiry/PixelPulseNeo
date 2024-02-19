from flask_restx import fields, Model
from pydantic import BaseModel
from typing import get_type_hints, List, Dict, Optional, Type, Tuple, Union, get_args


# XXX this code is broken because of a version missmatch on pydntic
# => to be revisited

def pydantic_to_restx_model(api, pydantic_model: BaseModel) -> Model:
    command = api.model(
        "Command",
        {
            "command_name": fields.String(
                required=True, default="time", description="The name of the command"
            ),
            "duration": fields.Integer(
                required=False,
                default=10,
                description="The duration in seconds to  run this command",
            ),
            "args": fields.List(
                fields.String(
                    required=False, description="command arguments (positional)"
                ),
                default=[],
            ),
            "kwargs": fields.Raw(required=False, description="command names arguments"),
        },
    )

    ## Define the model for the schedule (an array of schedule items)
    schedule_model = api.model(
        "Schedule",
        {
            "commands": fields.List(
                fields.Nested(command),
                required=True,
                description="The list of commands",
            ),
            "conditions": fields.List(
                fields.String(required=True, description="conditions", default="")
            ),
        },
    )

    return schedule_model
