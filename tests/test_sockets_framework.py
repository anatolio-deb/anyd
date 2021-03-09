from sockets_framework import __version__
from sockets_framework.core import Server, Client
from multiprocessing import Process
from tests import core as test_core

test_address = ("localhost", 3000)
test_server = Server(test_address, test_core)


def test_version():
    assert __version__ == '0.1.0'


def test_server_is_alive():
    global test_server
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    assert test_server_process.is_alive() is True
    test_server_process.kill()


def test_normal_request():
    global test_server
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    with Client(test_address) as call:
        response = call.commit("test_function", "echo")
    assert response == "echo"
    test_server_process.kill()


def test_not_implemented_function():
    global test_server
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    try:
        with Client(test_address) as call:
            call.commit("unknown_function", "echo")
    except NotImplementedError as e:
        assert isinstance(e, NotImplementedError)
    test_server_process.kill()


def test_multiple_requests():
    global test_server
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    with Client(test_address) as call:
        response = call.commit("test_function", "echo_one")
        assert response == "echo_one"
        response = call.commit("test_function", "echo_two")
        assert response == "echo_two"
    test_server_process.kill()
