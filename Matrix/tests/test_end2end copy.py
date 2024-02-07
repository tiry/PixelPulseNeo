import unittest
import threading
import requests
from Matrix.api.server import app
import time
from multiprocessing import Process
import os, signal

class FlaskServerTestCase(unittest.TestCase):

    @classmethod
    def __setUpClass(cls):
        # Start Flask server in a separate Process (Thread does hang)
        cls.server_process = Process(target=app.run, kwargs={"host": "0.0.0.0", "debug": False}, daemon=True)
        cls.server_process.start()

    @classmethod
    def __tearDownClass(cls):
        
        print("Tear down test: asking server to shut down")
        #time.sleep(5)
        # Shutdown the Flask server after tests
        requests.get('http://localhost:5000/shutdown')  # Assuming you have a shutdown route
        pid = cls.server_process.pid
        print("Tear down test: wait for server to exit")
        cls.server_process.terminate()
        print("Tear down test: wait for join")
        cls.server_process.join()
        cls.server_process.kill()
        print("Tear down test: completed")

        #os.kill(pid, signal.SIGINT)

    def test_api_endpoint(self):
        # Test the API endpoint
        
        print("will start request")
        time.sleep(2)
        
        response = requests.get('http://localhost:5000/commands')  
        self.assertEqual(response.status_code, 200)

        #print(response)


if __name__ == '__main__':
    unittest.main()
