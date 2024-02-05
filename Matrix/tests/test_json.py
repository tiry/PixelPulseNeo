import unittest
from Matrix.models.Commands import ScheduleModel, CommandEntry
from Matrix.models.encode import json_dumps, loadModel
from pydantic import BaseModel
import json

class TestIPCServer(unittest.TestCase):

    def getModel(self):
        commands=[]
        commands.append(CommandEntry(command_name="meteo"))
        commands.append(CommandEntry(command_name="news"))
        commands.append(CommandEntry(command_name="conway"))
        return ScheduleModel(commands=commands)

    def getJSONModel(self):
        json_str = """
            {"commands": [
                {"command_name": "meteo", "duration": 10.0, "args": [], "kwargs": {}}, 
                {"command_name": "news", "duration": 10.0, "args": [], "kwargs": {}}, 
                {"command_name": "conway", "duration": 10.0, "args": [], "kwargs": {}}], 
            "conditions": []}
        """
        return json.dumps(json.loads(json_str), indent=1)
        
    def test_convert_pydantic_to_json(self):
        
        schedule = self.getModel()
        json_str = json_dumps(schedule, indent=1)
        self.assertIsNotNone(json_str)

        self.assertEqual(json_str, self.getJSONModel())

        response_wrapper = {
            "success" : False,
            "error": None,
            "response" : None
        }

        response_wrapper["response"]=schedule
        json_str = json_dumps(response_wrapper, indent=1)
        

    
    def test_convert_json_to_pydantic(self):

        json_str = self.getJSONModel()
        schedule = loadModel(json_str, ScheduleModel)
        self.assertEqual(schedule, self.getModel())
        

        




