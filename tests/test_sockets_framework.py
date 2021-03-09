from sockets_framework import __version__
from sockets_framework.core import Server, Client
from multiprocessing import Process
from tests import core as test_core

test_address = ("localhost", 3000)
test_server = Server(test_address, test_core)
error = None


def test_version():
    assert __version__ == '0.1.0'


def test_server_is_alive():
    global test_server
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    assert test_server_process.is_alive() is True
    test_server_process.terminate()


def test_normal_request():
    global test_server, error
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    with Client(test_address) as call:
        response = call.commit("test_function", "echo")
    try:
        assert response == "echo"
    except AssertionError as e:
        error = e
    finally:
        test_server_process.terminate()
        if isinstance(error, AssertionError):
            raise error


def test_not_implemented_function():
    global test_server, error
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    try:
        with Client(test_address) as call:
            call.commit("unknown_function", "echo")
    except NotImplementedError as e:
        try:
            assert isinstance(e, NotImplementedError)
        except AssertionError as e:
            error = e
    finally:
        test_server_process.terminate()
        if isinstance(error, AssertionError):
            raise error


def test_multiple_requests():
    global test_server, error
    test_server_process = Process(target=test_server.start)
    test_server_process.start()
    with Client(test_address) as call:
        response_one = call.commit("test_function", "echo_one")
        response_two = call.commit("test_function", "echo_two")
    try:
        assert response_one == "echo_one"
        assert response_two == "echo_two"
    except AssertionError as e:
        error = e
    finally:
        test_server_process.terminate()
        if isinstance(error, AssertionError):
            raise error
