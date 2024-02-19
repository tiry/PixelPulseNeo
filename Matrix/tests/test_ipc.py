import unittest
from typing import Any
from Matrix.driver.ipc.server import IPCServer
from Matrix.driver.ipc.client import IPCClient


class TestIPCServer(unittest.TestCase):
    def test_execute_server_command(self):
        server = IPCServer()
        # Call with valid command
        response = server.execute_ipc_request("ping", [], {})
        self.assertTrue(response["success"])
        self.assertEqual("pong", response["response"])

        # Call dynamic command
        pparams: list = [1, 2, 3]
        nparams: dict[str, int] = {"a": 7}
        response: dict[str, Any] = server.execute_ipc_request("echo", pparams, nparams)
        self.assertTrue(response["success"])
        res: Any = response["response"].split("\n")
        self.assertEqual("OK", res[0])
        self.assertEqual(str(tuple(pparams)), res[1])
        self.assertEqual(str(nparams), res[2])
        self.assertTrue(f"{str(tuple(pparams))}" in str(response["response"]))  # type: ignore

    def test_invalid_command(self):
        server = IPCServer()

        # Call with invalid command
        response: dict[str, Any] = server.execute_ipc_request("invalid", [], {})
        self.assertFalse(response["success"])
        self.assertIsNotNone(response["error"])


class TestIPCClientServer(unittest.TestCase):
    def test_execute_server_command(self):
        client = IPCClient()

        response = client.send_command("ping")
        self.assertTrue(response["success"])
        self.assertEqual("pong", response["response"])

        # Call dynamic command
        pparams: list[int] = [1, 2, 3]
        nparams: dict[str, int] = {"a": 7}
        response: Any = client.send_command("echo", *pparams, **nparams)
        self.assertTrue(response["success"])
        res: Any = response["response"].split("\n")
        self.assertEqual("OK", res[0])
        self.assertEqual(str(tuple(pparams)), res[1])
        self.assertEqual(str(nparams), res[2])
        self.assertTrue(f"{str(tuple(pparams))}" in response["response"])
        # client.send_command("dummy2", 1, foo ="beer")

        client.send_command("exit")
        # client.disconnect()


if __name__ == "__main__":
    unittest.main()
