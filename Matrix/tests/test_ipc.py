import unittest
from Matrix.driver.ipc.server import IPCServer
from Matrix.driver.ipc.client import IPCClient

class TestIPCServer(unittest.TestCase):

    def test_execute_server_command(self):
        
        server = IPCServer()
        # Call with valid command
        response = server.execute_ipc_request("ping", [], {})
        self.assertTrue(response["success"])
        self.assertEqual("pong",response["response"])
        
        # Call dynamic command
        pparams = (1,2,3)
        nparams = {"a":7}
        response = server.execute_ipc_request("echo", pparams, nparams)
        self.assertTrue(response["success"])
        res = response["response"].split("\n")
        self.assertEqual("OK" , res[0])
        self.assertEqual(str(pparams) , res[1])
        self.assertEqual(str(nparams) , res[2])
        self.assertTrue(f"{str(pparams)}" in  response["response"])
        
    def test_invalid_command(self):

        server = IPCServer()
        
        # Call with invalid command
        response = server.execute_ipc_request("invalid", [], {}) 
        self.assertFalse(response["success"])
        self.assertTrue(response["error"]!=None)


class TestIPCClientServer(unittest.TestCase):

    def test_execute_server_command(self):
        
        client = IPCClient()

        response = client.send_command("ping")
        self.assertTrue(response["success"])
        self.assertEqual("pong",response["response"])

        # Call dynamic command
        pparams = (1,2,3)
        nparams = {"a":7}
        response = client.send_command("echo", *pparams, **nparams)
        self.assertTrue(response["success"])
        res = response["response"].split("\n")
        self.assertEqual("OK" , res[0])
        self.assertEqual(str(pparams) , res[1])
        self.assertEqual(str(nparams) , res[2])
        self.assertTrue(f"{str(pparams)}" in  response["response"])
        #client.send_command("dummy2", 1, foo ="beer")

        client.disconnect()



if __name__ == '__main__':
    unittest.main()