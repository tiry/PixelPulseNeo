from Matrix import config
from Matrix.driver.factory import IPCClientSingleton
import argparse
import unittest
import requests
from Matrix.api.server import app
import time
from multiprocessing import Process
from PIL import Image
from io import BytesIO
import json
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ipc", help="run end to end test with IPC communication", action="store_true"
    )
    args = parser.parse_args()

    print("################################################")
    if not args.ipc:
        print("Running test with No IPC")
        config.USE_IPC = False
    else:
        print("Running test with IPC")
        config.USE_IPC = True
        # Make the IPC Client automatically start the server
        IPCClientSingleton.start_server_if_needed=True
        old_sys_argv = sys.argv
        sys.argv = [old_sys_argv[0]]
    print("################################################")


class FlaskServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Flask server in a separate Process (Thread does hang)
        cls.server_process = Process(
            target=app.run, kwargs={"host": "0.0.0.0", "debug": False}, daemon=True
        )
        cls.server_process.start()
        time.sleep(1)
        print("################################################")
        print("################################################")
        print("Test API Server Started ")
        print(f"    use IPC = {config.USE_IPC}")

    @classmethod
    def tearDownClass(cls):
        print("Tear down test: asking server to shut down")
        # Shutdown the Flask server after tests
        requests.get(
            "http://localhost:5000/api/shutdown", timeout=5
        )  # Assuming you have a shutdown route
        print("Tear down test: wait for server to exit")
        cls.server_process.terminate()
        print("Tear down test: wait for join")
        cls.server_process.join()
        cls.server_process.kill()
        print("Tear down test: completed")

        # os.kill(pid, signal.SIGINT)

    def test_can_list_commands(self):
        print("################################################")
        print("testing commands API")

        response = requests.get("http://localhost:5000/api/commands", timeout=5)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        cmds = response.json()
        self.assertTrue(len(cmds) > 0)

        self.assertTrue("name" in cmds[0].keys())
        self.assertTrue("description" in cmds[0].keys())
        self.assertTrue("screenshots" in cmds[0].keys())

        self.assertEqual(list, type(cmds[0]["screenshots"]))

    def test_can_list_schedules(self):
        print("################################################")
        print("testing schedules API")

        response = requests.get("http://localhost:5000/api/schedules",timeout=5)
        response.raise_for_status()

        self.assertEqual(response.status_code, 200)

        schedules = response.json()
        self.assertTrue(len(schedules) > 0)
        self.assertEqual(str, type(schedules[0]))

    def test_can_instrospect_command(self):
        target_command = "mta"
        print("################################################")
        print("testing command API")

        response = requests.get("http://localhost:5000/api/commands", timeout=5)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)
        cmds = response.json()

        for cmd in cmds:
            # check one known command
            if cmd["name"] == target_command:
                self.assertTrue(len(cmd["screenshots"]) > 0)

            # now download the images
            for name in cmd["screenshots"]:
                response = requests.get(
                    f"http://localhost:5000/api/screenshots/{target_command}/{name}", timeout=5
                )
                self.assertEqual(response.status_code, 200)
                i = Image.open(BytesIO(response.content))
                self.assertTrue(i.width > 10)

    def test_exec_command(self):
        target_command = "time"
        print("################################################")
        print("testing command API")

        response = requests.post(f"http://localhost:5000/api/command/{target_command}", timeout=5)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)
        res = response.json()

        # XXX Get logs to verify
        print(res)

    def test_schedule_CRU(self):
        marker = f"token{time.time()}"
        src_schedule = {
            "commands": [
                {
                    "command_name": "time",
                    "duration": 1.0,
                    "args": [marker],
                    "kwargs": {},
                },
            ],
            "conditions": [],
        }
        src_schedule_json = json.loads(json.dumps(src_schedule))

        schedule_name = "testingschedule"

        headers = {"content-type": "application/json"}

        response = requests.post(
            f"http://localhost:5000/api/schedule/{schedule_name}",
            headers=headers,
            data=json.dumps(src_schedule_json), timeout=5
        )
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        # now get the schedule back

        response = requests.get(f"http://localhost:5000/api/schedule/{schedule_name}", timeout=5)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)
        new_schedule_json = response.json()

        self.assertEqual(json.dumps(src_schedule_json), json.dumps(new_schedule_json))


if __name__ == "__main__":
    unittest.main()
