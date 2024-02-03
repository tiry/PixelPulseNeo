import unittest
import time
import tempfile
import os
import json


from Matrix.driver.executor import CommandExecutor
from Matrix.models.Commands import CommandEntry, CommandExecutionLog

class TestCmdExecutor(unittest.TestCase):

    def test_log_entry(self):
        command_entry= CommandEntry(command_name="cmd01", duration=5)
        res = "OK"
        log = CommandExecutionLog(command=command_entry.copy(deep=True), result=res, effective_duration=1.1)
        self.assertIsNotNone(log)
        self.assertEqual("cmd01", log.command.command_name)
        self.assertEqual(5, log.command.duration)
        self.assertEqual(res, log.result)
        self.assertIsNotNone(log.execution_date)
        self.assertIsNotNone(log.execution_time)
        #print(log)

    def test_ls(self):
        executor = CommandExecutor(schedule_file=None)
        cmds = executor.list_commands()
        self.assertTrue(len(cmds)>0)
        executor.stop()


    def test_exec(self):
        
        executor = CommandExecutor(schedule_file=None)
        
        executor.execute_now("time", 0.1)
        
        time.sleep(1)

        log = executor.get_audit_log()
        self.assertEqual(1, len(log))

        res = log[0].result
        self.assertIsNotNone(res)
        
        print(f"RETURN => {res}")


        executor.stop()



    def test_exec_multi(self):
        
        executor = CommandExecutor(schedule_file=None)
        
        args = ["Yo"]
        executor.execute_now("faker", 0.1, args=args, kwargs = {"mock_return": "EchoArgs"})        
        time.sleep(1)

        log = executor.get_audit_log()
        self.assertEqual(1, len(log))

        res = log[0].result
        self.assertIsNotNone(res)
        self.assertEqual(str(args), res)        
        
        executor.execute_now("faker", 0.1, args=args, kwargs = {"mock_return": "Exception"})
        time.sleep(1)

        log = executor.get_audit_log()
        self.assertEqual(2, len(log))
        self.assertIsNotNone(log[1].error)
        
        executor.stop()



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
                    }                
                }
            }

        # Write JSON data to the file
        json.dump(data, temp_file)
        temp_file.flush()  # Ensure data is written to the file
        temp_file.close()
        return temp_file.name
        


    def test_schedule_and_enqueue(self):
        
        schedule_file = self.get_test_schedule_file()

        executor = CommandExecutor(schedule_file=schedule_file)
        # give  time for the scheduler to load
        time.sleep(1)
        schedule = executor.get_schedule()
        #print(f"schedule = {schedule}")
        
        # give time to execute
        time.sleep(2)
        log = executor.get_audit_log()
        self.assertTrue(len(log)>2)

        executor.stop(interrupt=True)

        os.remove(schedule_file)






        
        