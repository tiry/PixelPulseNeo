import unittest
import time
from Matrix.driver.executor import CommandExecutor
from Matrix.models.Commands import CommandEntry, CommandExecutionLog


class TestCmdExecutor(unittest.TestCase):
    def test_log_entry(self):
        command_entry = CommandEntry(command_name="cmd01", duration=5)
        res = "OK"
        log = CommandExecutionLog(
            command=command_entry.copy(deep=True), result=res, effective_duration=1.1
        )
        self.assertIsNotNone(log)
        self.assertEqual("cmd01", log.command.command_name)
        self.assertEqual(5, log.command.duration)
        self.assertEqual(res, log.result)
        self.assertIsNotNone(log.execution_date)
        self.assertIsNotNone(log.execution_time)
        # print(log)

    def test_ls(self):
        executor = CommandExecutor(schedule_file=None)
        cmds = executor.list_commands()
        self.assertTrue(len(cmds) > 0)
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
        executor.execute_now(
            "faker", 0.1, args=args, kwargs={"mock_return": "EchoArgs"}
        )
        time.sleep(1)

        log = executor.get_audit_log()
        self.assertEqual(1, len(log))

        res = log[0].result
        self.assertIsNotNone(res)
        self.assertEqual(str(args), res)

        executor.execute_now(
            "faker", 0.1, args=args, kwargs={"mock_return": "Exception"}
        )
        time.sleep(1)

        log = executor.get_audit_log()
        self.assertEqual(2, len(log))
        self.assertIsNotNone(log[1].error)

        executor.stop()
