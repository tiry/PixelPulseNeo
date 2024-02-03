import unittest
import time
import tempfile
import os
import json


from Matrix.driver.executor import CommandExecutor
from Matrix.models.Commands import CommandEntry, CommandExecutionLog

class TestEnqueeCmd(unittest.TestCase):

    def get_test_schedule_file(self):

        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=".json", prefix="schedule-")
       
        data = {
                "playlists": {
                    "default": {
                        "commands": [
                            {
                                "command_name": "time",
                                "duration": 0.5,
                                "args": [],
                                "kwargs": {}
                            },
                            {
                                "command_name": "faker",
                                "duration": 0.5,
                                "args": ["oho", "nino"],
                                "kwargs": {"mock_return": "EchoArgs"}
                            },
                        ],
                        "conditions": []
                    },        
                    "slow": {
                        "commands": [
                            {
                                "command_name": "time",
                                "duration": 10,
                                "args": [],
                                "kwargs": {}
                            },
                            {
                                "command_name": "time",
                                "duration": 5,
                                "args": [],
                                "kwargs": {}
                            },
                        ],
                        "conditions": []
                    },
                    "smoke_test": {
                        "commands": [
                            {
                                "command_name": "mta",
                                "duration": 3,
                                "args": [],
                                "kwargs": {"pause_frames": 10}
                            },
                            {
                                "command_name": "meteo",
                                "duration": 4,
                                "args": [],
                                "kwargs": {}
                            },
                            {
                                "command_name": "citibikes",
                                "duration": 4,
                                "args": [],
                                "kwargs": {}
                            },
                            {
                                "command_name": "conway",
                                "duration": 4,
                                "args": [],
                                "kwargs": {}
                            },
                            {
                                "command_name": "news",
                                "duration": 4,
                                "args": [],
                                "kwargs": {}
                            },

                        ],
                        "conditions": []
                    }        
                }
            }

        # Write JSON data to the file
        json.dump(data, temp_file)
        temp_file.flush()  # Ensure data is written to the file
        temp_file.close()
        return temp_file.name
        


    def _test_schedule_load(self):
        
        schedule_file = self.get_test_schedule_file()

        executor = CommandExecutor(schedule_file=schedule_file)

        # wait for the scheduler to start and to run at least 2 cmds
        executor._wait_for_executions(2)

        schedule = executor.get_schedule()
        
        log = executor.get_audit_log()
        print(f"LOGS =>{log}")
        self.assertTrue(len(log)>=2)

        executor.stop(interrupt=True)

        os.remove(schedule_file)
    
    def _test_schedule_and_enqueue(self):
        
        schedule_file = self.get_test_schedule_file()

        executor = CommandExecutor(schedule_file=schedule_file)
        executor.load_schedule("slow")
        schedule = executor.get_schedule()
        print(schedule)

        time.sleep(1)
        executor.execute_now(command_name ="faker", duration = 0.5, args =["Bypass"], kwargs =  {"mock_return": "EchoArgs"}, interrupt=True)
        
        # wait for the scheduler to start and to run at least 2 cmds
        executor._wait_for_executions(2)

        log = executor.get_audit_log()

        self.assertEqual(10, log[1].command.duration)
        self.assertLess(log[1].effective_duration, 10)

        print(f"LOGS =>{log}")
        self.assertTrue(len(log)>=2)
        print(f"LAST =>{log[-1]}")

        executor.stop(interrupt=True)

        os.remove(schedule_file)

    def test_default_schedule(self):

        schedule_file = self.get_test_schedule_file()

        executor = CommandExecutor(schedule_file=schedule_file)
        executor.load_schedule("smoke_test")
        executor._wait_for_executions(6, timeout_seconds=120)

        log = executor.get_audit_log()

        for entry in log:
            self.assertIsNone(entry.error)

        executor.stop(interrupt=True)
        os.remove(schedule_file)



    






        
        