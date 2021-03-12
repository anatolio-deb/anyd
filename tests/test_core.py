import pytest
from sockets_framework import __version__
from sockets_framework.core import Server, Client
from multiprocessing import Process
import importlib
import pathlib
from types import ModuleType
import sys


@pytest.fixture
def fixture03(tmp_path: pathlib.Path):
    content = '''
def test_function(test_arg: str):
    return test_arg
'''
    pkg = tmp_path / "test_pkg"
    pkg.mkdir()
    sys.path.append(pkg.as_posix())
    mod = pkg / "test_core.py"
    mod.write_text(content)
    init = pkg / "__init__.py"
    init.touch()
    assert mod.read_text() == content
    test_core = importlib.import_module('test_core')
    assert isinstance(test_core, ModuleType)
    return test_core


@pytest.fixture
def fixture01():
    return ("localhost", 3000)


@pytest.fixture
def fixture02(request, fixture01, fixture03):
    test_server = Server(fixture01, fixture03)
    test_server_process = Process(target=test_server.start)

    def terminate_server():
        test_server.close()
        test_server_process.terminate()

    request.addfinalizer(terminate_server)
    return test_server_process


def test_version():
    assert __version__ == '0.1.0'


def test_case01(fixture02):
    """Server is running

    :param fixture02: The server's process
    :type fixture02: multiprocessing.Process
    """
    fixture02.start()
    assert fixture02.is_alive() is True


def test_case02(fixture01, fixture02):
    """Normal request

    :param fixture01: The server's address
    :type fixture01: tuple
    :param fixture02: The server's process
    :type fixture02: multiprocessing.Process
    """
    fixture02.start()
    with Client(fixture01) as call:
        response = call.commit("test_function", "echo")
    assert response == "echo"


def test_case03(fixture01, fixture02):
    """NotImplementedError

    :param fixture01: The server's address
    :type fixture01: tuple
    :param fixture02: The server's process
    :type fixture02: multiprocessing.Process
    """
    fixture02.start()
    with Client(fixture01) as call:
        with pytest.raises(NotImplementedError):
            call.commit("unknown_function", "echo")


def test_case04(fixture01, fixture02):
    """Multiple requests.

    :param fixture01: The server's address
    :type fixture01: tuple
    :param fixture02: The server's process
    :type fixture02: multiprocessing.Process
    """
    fixture02.start()
    with Client(fixture01) as call:
        response = call.commit("test_function", "echo_one")
        assert response == "echo_one"
        response = call.commit("test_function", "echo_two")
        assert response == "echo_two"
