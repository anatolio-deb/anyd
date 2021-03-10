from sockets_framework.core import Client, Server
import unittest
from tests import core as test_core
from multiprocessing import Process


class TesClass01(unittest.TestCase):
    test_address = ("localhost", 3000)
    test_server = Server(test_address, test_core)

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_server_process = Process(target=cls.test_server.start)
        cls.test_server_process.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.test_server.close()
        cls.test_server_process.terminate()

    def test_case01(self):
        """Server is running.
        """
        self.assertIs(self.test_server_process.is_alive(), True)

    def test_case02(self):
        """Normal request.
        """
        with Client(self.test_address) as session:
            response = session.commit("test_function", "echo")
        self.assertEqual(response, "echo")

    def test_case03(self):
        """NotImplementedError.
        """
        with self.assertRaises(NotImplementedError):
            with Client(self.test_address) as call:
                call.commit("unknown_function", "echo")

    def test_case04(self):
        with Client(self.test_address) as call:
            response = call.commit("test_function", "echo_one")
            self.assertEqual(response, "echo_one")
            response = call.commit("test_function", "echo_two")
            self.assertEqual(response, "echo_two")
