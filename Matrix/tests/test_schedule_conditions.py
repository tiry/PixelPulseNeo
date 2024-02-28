import unittest
import tempfile
import os
import json
from Matrix.driver.scheduler import Scheduler
from Matrix.models.Commands import ScheduleModel, CommandEntry
from Matrix.driver.context import NAMED_CONDITIONS, SHARED_CONTECT, eval_condition

PLAYLIST_NAME = "default_test_schedule"

"""Test cases for the "low level" Scheduler module."""

#TestVariable:bool = True
#IsDay : bool = True
#TestVariable2 = None

class TestScheduleConditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        
        SHARED_CONTECT["test_var"] = True
        SHARED_CONTECT["is_day"] = True
        SHARED_CONTECT["test_var2"] = None
        
        #Override some conditions
        NAMED_CONDITIONS["TEST_CONDITION"] =  "test_var is True"
        NAMED_CONDITIONS["DAY"] =  "is_day==True"
        NAMED_CONDITIONS["NIGHT"] =  "is_day==False"
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w+", suffix=".json", prefix="schedule-"
        )
        # print("Temporary file created at:", temp_file.name)

        cls.temp_file_name = temp_file.name

        # Create schedule for test
        data = {
            "playlists": {
                "default": {
                    "commands": [
                        {
                            "command_name": "mta",
                            "duration": 10,
                            "args": [],
                            "kwargs": {},
                        },
                        {
                            "command_name": "meteo",
                            "duration": 10,
                            "args": [],
                            "kwargs": {},
                        },
                    ],
                    "conditions": [],
                },
                "night": {
                    "commands": [
                        {
                            "command_name": "meteo",
                            "duration": 10,
                            "args": [],
                            "kwargs": {},
                        },
                    ],
                    "conditions": ['night'],
                },
                "day": {
                    "commands": [
                        {
                            "command_name": "meteo",
                            "duration": 10,
                            "args": [],
                            "kwargs": {},
                        },
                    ],
                    "conditions": ['day'],
                },
            }
        }

        # Write JSON data to the file
        json.dump(data, temp_file)
        temp_file.flush()  # Ensure data is written to the file
        temp_file.close()
        cls.temp_file = temp_file

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.temp_file_name)
        # print("Temporary file deleted:", cls.temp_file_name)

    def test_conditions(self):
        
        self.assertTrue(eval_condition("test_var2 is None"))
        SHARED_CONTECT["test_var2"] = 1
        self.assertFalse(eval_condition("test_var2 is None"))
        self.assertTrue(eval_condition("test_var2 ==1"))
        
        self.assertTrue(eval_condition("test_condition"))
        SHARED_CONTECT["test_var"] = False
        self.assertFalse(eval_condition("test_condition"))

        self.assertTrue(eval_condition("day"))
        self.assertFalse(eval_condition("night"))
        SHARED_CONTECT["is_day"] = False
        self.assertFalse(eval_condition("day"))
        self.assertTrue(eval_condition("night"))
        
    def test_load_schedule(self):
        
        SHARED_CONTECT["is_day"] = True

        schedule_file = self.__class__.temp_file_name
        scheduler = Scheduler(schedule_file=schedule_file)
        
        playlist = scheduler.get_next_catalog()
        self.assertEqual("day", playlist)
        
        SHARED_CONTECT["is_day"] = False
        playlist = scheduler.get_next_catalog()
        self.assertEqual("night", playlist)

        SHARED_CONTECT["is_day"] = None
        playlist = scheduler.get_next_catalog()
        self.assertEqual("default", playlist)
        

if __name__ == "__main__":
    unittest.main()
