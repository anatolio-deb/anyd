from multiprocessing.connection import Client as __Client, Listener
import time
from types import ModuleType, FunctionType
import inspect
from contextlib import contextmanager
from typing import Any

SIGEND = b"SIGEND"


def receive(address: str or tuple, authkey: bytes = None) -> Any:
    while True:
        try:
            with __Client(address, authkey=authkey) as conn:
                response = conn.recv()
        except ConnectionRefusedError:
            time.sleep(0.1)
        else:
            return response


class Server(Listener):
    def __init__(self,
                 listen_address: str or tuple,
                 core: ModuleType,
                 authkey: bytes = None) -> None:
        super().__init__(address=listen_address, authkey=authkey)
        self.core = inspect.getmembers(core, predicate=inspect.isfunction)

    def start(self) -> None:
        while True:
            with self.accept() as conn:
                conn.send(self.last_accepted)
            while True:
                request = receive(self.last_accepted)
                if request[0] in [t[0] for t in self.core]:
                    for name, func in self.core:
                        if name == request[0]:
                            response = FunctionType(
                                code=func.__code__,
                                globals=func.__globals__,
                                argdefs=inspect.signature(func).bind(
                                    *request[1], **request[2]).args)()
                elif request[0] == SIGEND:
                    response = SIGEND
                else:
                    response = NotImplementedError(request[0])
                with Listener(address=self.last_accepted) as listener:
                    with listener.accept() as conn:
                        conn.send(response)
                if response == SIGEND:
                    break


class _Client(Listener):
    def __init__(self, server_address, autkey: bytes = None) -> None:
        self.local_address = receive(server_address, autkey)
        super().__init__(address=self.local_address)

    def commit(self, core_function: str, *args, **kwargs) -> Any:
        request = (core_function, args, kwargs)
        with self.accept() as conn:
            conn.send(request)
        self.close()
        response = receive(self.local_address)
        super().__init__(self.local_address)
        if isinstance(response, NotImplementedError):
            raise response
        return response


@contextmanager
def Client(server_address: str or tuple) -> _Client:
    client = _Client(server_address)
    try:
        yield client
    finally:
        response = client.commit(SIGEND)
        if response == SIGEND:
            client.close()
            del client
        else:
            raise RuntimeError("The session is not closed propery")
