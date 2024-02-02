import unittest
import time

from Matrix.driver.executor import CommandExecutor

class TestCmdExecutor(unittest.TestCase):

    def _test_ls(self):
        
        executor = CommandExecutor(scheduler_enabled=False)
        
        cmds = executor.list_commands()
        self.assertTrue(len(cmds)>0)


    def _test_schedule(self):
        
        executor = CommandExecutor(scheduler_enabled=False)        
        schedule = executor.load_schedule()
        self.assertIsNotNone(schedule)

        print(schedule)
        schedule = executor.get_schedule()
        self.assertIsNotNone(schedule)


    def test_exec(self):
        
        executor = CommandExecutor(scheduler_enabled=False)        
        
        res = executor.execute_now("time", 1)
        print(res)
        #server_ts = int(res.split(".")[0])
        #client_ts = int(time.time())

        #print(client_ts-server_ts)

