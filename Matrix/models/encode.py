from typing import Any
import json
from pydantic import BaseModel


def json_dumps(obj, indent=None):
    return json.dumps(obj, cls=PydanticJsonEncoder, indent=indent)


class PydanticJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return json.loads(obj.model_dump_json())
        return json.JSONEncoder.default(self, obj)


def loadModel(json_str, pydantic_model):
    return pydantic_model.model_validate_json(json_str)


def deepcopy(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_copy(deep=True)
    else:
        return obj.copy()
