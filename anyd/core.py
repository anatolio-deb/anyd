from __future__ import annotations

import logging
from multiprocessing.connection import Client, Listener
from types import FunctionType
from typing import Any, Tuple, Union

logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    # datefmt="%m/%d/%Y:%I:%M:%S",
    level=logging.INFO,
)

SIGENDS: bytes = b"SIGENDS"


class Appd(Listener):
    """Inherit form this class and define your methods:

    class MyServer(Appd):
        def my_echo_method(self, my_arg):
            return my_arg
    """

    response: Any = None
    request: Tuple = ()
    _api: dict = {}

    def api(self, func: FunctionType):
        self._api[func.__name__] = func

    def start(self):
        while True:
            local = f"{self.address[0]}:{self.address[1]}"

            logging.info("[LST] -> %s", local)

            with self.accept() as conn:

                remote = f"{self.last_accepted[0]}:{self.last_accepted[1]}"

                logging.info("[SES] <- %s", remote)

                while self.response != SIGENDS:
                    try:
                        self.request = conn.recv()
                    except EOFError:
                        break

                    logging.info("[REQ] <- %s + %s", remote, self.request)

                    if self.request[0] in self._api.keys():
                        self.response = self._api[self.request[0]](
                            *self.request[1], **self.request[2]
                        )
                    elif self.request == SIGENDS:
                        self.response = SIGENDS
                    else:
                        self.response = NotImplementedError(self.request[0])

                    conn.send(self.response)

                    logging.info("[RES] + %s -> %s", self.response, remote)
                else:
                    self.response = None

                logging.info("[SES] x %s", remote)


class _Client:
    """Wraps multiprocessing.connection.Client"""

    request: Tuple = ()
    response: Any = None

    def __init__(
        self,
        address: Union[str, Tuple[str, int]],
        family: str = None,
        authkey: bytes = None,
    ):
        self.conn = Client(address, family, authkey)

    def commit(self, endpoint: str, *args, **kwargs) -> Any:
        """Used to form and send the request to the Appd,
        then accepts the response from it.

        Args:
            method (str): A name of the method to call on the Appd

        Raises:
            response: The value returned by the method on the Appd
        """
        self.request = (endpoint, args, kwargs)
        self.conn.send(self.request)
        self.response = self.conn.recv()

        if isinstance(self.response, Exception):
            raise self.response

        return self.response

    def end_session(self):
        self.conn.send(SIGENDS)
        self.response = self.conn.recv()

        try:
            if self.response != SIGENDS:
                raise ValueError(f"Improperly closed session: {self.response}")
        finally:
            self.conn.close()


class ClientSession:
    """A Context Manger for client"""

    def __init__(
        self,
        address: Union[str, Tuple[str, int]],
        family: str = None,
        authkey: bytes = None,
    ):
        self.client = _Client(address, family, authkey)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.end_session()
