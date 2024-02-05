from flask_restx import fields, Model
from pydantic import BaseModel
from typing import get_type_hints, List, Dict, Optional, Type, Tuple, Union,  get_args
from datetime import datetime
import traceback


# XXX this code is broken because of a version missmatch on pydntic
# => to be revisited

def __pydantic_field_to_restx_field(api, field_type):
    """Map a Pydantic field type to a Flask-RestX field type."""
    if issubclass(field_type, str):
        return fields.String
    elif issubclass(field_type, int):
        return fields.Integer
    elif issubclass(field_type, float):
        return fields.Float
    elif issubclass(field_type, bool):
        return fields.Boolean
    elif issubclass(field_type, list):
        # Assuming a list of strings for simplicity; extend as needed
        return fields.List(fields.String)
    elif issubclass(field_type, dict):
        # Assuming a dict with string keys and values for simplicity; extend as needed
        return fields.Raw
    elif issubclass(field_type, BaseModel):
        # Nested Pydantic model
        return pydantic_to_restx_model(api, field_type)
    else:
        # Default to raw field for unknown types
        return fields.Raw

def ___pydantic_field_to_restx_field(api, field_type: Type):
    """Map a Pydantic field type to a Flask-RestX field type."""
    origin_type = getattr(field_type, '__origin__', None)

    try:
        if field_type is str or origin_type is str:
            return fields.String
        elif field_type is int or origin_type is int:
            return fields.Integer
        elif field_type is float or origin_type is float:
            return fields.Float
        elif field_type is bool or origin_type is bool:
            return fields.Boolean
        elif field_type is list or origin_type is list:
            # Assuming a list of strings for simplicity; extend as needed
            return fields.List(fields.String)
        elif field_type is dict or origin_type is dict:
            # Assuming a dict with string keys and values for simplicity; extend as needed
            return fields.Raw
        elif field_type is Tuple or origin_type is Tuple:
            # Assuming a tuple of strings for simplicity; extend as needed
            # Tuples are represented as lists in the Flask-RestX model
            return fields.List(fields.String)
        elif issubclass(field_type, BaseModel):
            # Nested Pydantic model
            return pydantic_to_restx_model(api, field_type)
        else:
            # Default to raw field for unknown types
            return fields.Raw
    except Exception as e:
        print(f"Unable to map field of type {field_type}")
        return fields.Raw


def pydantic_field_to_restx_field(api, field_type: Type):
    """Map a Pydantic field type to a Flask-RestX field type."""
    origin_type = getattr(field_type, '__origin__', field_type)
    
    print(f"called with type = {field_type} {origin_type}")
    try:
        # Handle Optional types and Union types (like Optional[X])
        if origin_type is Union:
            # Extract the non-None type from Union[X, NoneType]
            field_types = get_args(field_type)
            non_none_types = [t for t in field_types if t is not type(None)]
            field_type = non_none_types[0] if non_none_types else field_type
            origin_type = getattr(field_type, '__origin__', field_type)

        if origin_type in (str, int, float, bool):
            type_mapping = {
                str: fields.String,
                int: fields.Integer,
                float: fields.Float,
                bool: fields.Boolean
            }
            return type_mapping[origin_type]
        elif origin_type is List or origin_type is list:
            # Handle lists with specific element types
            element_type = get_args(field_type)[0]
            target_restx_type = pydantic_field_to_restx_field(api, element_type)
            print(f"List item type = {element_type} => {target_restx_type}")
            return fields.List(target_restx_type)
        elif origin_type is Dict or origin_type is dict:
            # Handle dictionaries
            # For simplicity, assuming string keys and string values; extend as needed
            return fields.Raw()
        elif origin_type is Tuple or origin_type is tuple:
            # Handle tuples
            # For simplicity, assuming all elements are of the same type; extend as needed
            element_type = get_args(field_type)[0]
            return fields.List(pydantic_field_to_restx_field(api, element_type))
        elif issubclass(field_type, BaseModel):
            # Nested Pydantic model
            return pydantic_to_restx_model(api, field_type)
        else:
            # Default to raw field for unknown types
            return fields.Raw()
    except Exception as e:
        print(f"Unable to map field of type {field_type} {origin_type}: {e}")
        print(traceback.format_exc())
        return fields.Raw()


            
def pydantic_to_restx_model(api, pydantic_model: BaseModel) -> Model:
    """
    Converts a Pydantic model into a Flask-RestX model.

    :param api: The Flask-RestX Api instance
    :param pydantic_model: The Pydantic model class to convert
    :return: A Flask-RestX model
    """
    restx_fields = {}

    for field_name, field_type in get_type_hints(pydantic_model).items():
        # Handle Optional fields
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Optional:
            field_type = field_type.__args__[0]

        restx_field = pydantic_field_to_restx_field(api, field_type)
        restx_fields[field_name] = restx_field
        #restx_fields[field_name] = restx_field(description=field_name)

    return fields.Nested(api.model(pydantic_model.__name__, restx_fields))

def pydantic_to_restx_model(api, pydantic_model: BaseModel) -> Model:

    command = api.model('Command', {
        'command_name': fields.String(required=True, default="time", description='The name of the command'),
        'duration': fields.Integer(required=False, default=10, description='The duration in seconds to  run this command'),
        'args': fields.List(fields.String(required=False, description='command arguments (positional)'), default=[]),
        'kwargs': fields.Raw(required=False, description='command names arguments') ,
    })

    ## Define the model for the schedule (an array of schedule items)
    schedule_model = api.model('Schedule', {
        'commands': fields.List(fields.Nested(command), required=True, description='The list of commands'),
        'conditions': fields.List(fields.String(required=True, description='conditions', default=""))
    })

    return schedule_model

