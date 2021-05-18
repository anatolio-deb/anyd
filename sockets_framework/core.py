from __future__ import annotations

import inspect
import logging
import time
from multiprocessing.connection import Client, Listener
from types import TracebackType
from typing import Any, Iterable, Optional, Tuple, Type

logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s] %(message)s",
    datefmt="%I:%M:%S",
    level=logging.DEBUG,
)
SIGENDSESSION = b"SIGENDSESSION"


def recv_from(*args, **kwargs):
    data: Any = None
    max_retries: int = 100
    while not data and max_retries > 0:
        try:
            with Client(*args, **kwargs) as conn:
                data = conn.recv()
        except ConnectionRefusedError:
            max_retries -= 1
            if max_retries == 0:
                raise
            time.sleep(0.01)
        else:
            return data


class BaseServer(Listener):
    """Inherit form this class and define your methods:

    class MyServer(BaseServer):
        def my_echo_method(self, my_arg):
            return my_arg
    """

    response: Any = None
    request: Tuple[str][Iterable] = ()

    def start(self):
        """Starts the server instance, listens for incoming connections, \
        handle's client's requets, calls appropriate method."""
        while True:
            logging.info("Listening at %s:%s", self.address[0], self.address[1])

            with self.accept() as conn:
                logging.info(
                    "Incoming connection from %s:%s",
                    self.last_accepted[0],
                    self.last_accepted[1],
                )

                conn.send(self.last_accepted)
            while self.response != SIGENDSESSION and not isinstance(
                self.response, (NotImplementedError, ValueError)
            ):
                logging.info(
                    "Session loop started for client: %s:%s",
                    self.last_accepted[0],
                    self.last_accepted[1],
                )

                try:
                    self.request = recv_from(address=self.last_accepted)
                except ConnectionRefusedError as exception:
                    logging.exception(exception)
                    self.response = SIGENDSESSION
                else:
                    logging.info(
                        "Accepted request %s from %s:%s",
                        self.request,
                        self.last_accepted[0],
                        self.last_accepted[1],
                    )

                    self._set_response()

                    with self.accept() as conn:
                        logging.info(
                            "Sending response: %s to %s:%s",
                            self.response,
                            self.last_accepted[0],
                            self.last_accepted[1],
                        )

                        conn.send((self.response, self.last_accepted))

            self.response = None

            logging.info(
                "Ending session for %s:%s",
                self.last_accepted[0],
                self.last_accepted[1],
            )

    def _set_response(self):
        if self.request[0] in dir(self):
            for name, link in inspect.getmembers(self, predicate=inspect.ismethod):
                if name == self.request[0] and name not in dir(super):
                    self.response = link(*self.request[1], **self.request[2])
                    break
                self.response = ValueError(
                    f"The method name {self.request[0]} is unacceptable, "
                    "consider renaming your method."
                )
        elif self.request[0] == SIGENDSESSION:
            self.response = SIGENDSESSION
        else:
            self.response = NotImplementedError(self.request[0])


class _Client(Listener):
    """Used with BaseServer instances. Gets communication address from the BaseServer,
    Sends a request to the BaseServer's listening address, then opens a listener on
    the received address to accept the response from the BaseServer"""

    response: Any = None
    request: Tuple[str][Iterable] = ()

    def __init__(
        self, address: str | Tuple[str, int], family: str | None, authkey: bytes | None
    ) -> None:
        self.session_socket = recv_from(address, family, authkey)
        # NOTE: might except OSError here
        super().__init__(address=self.session_socket)
        self.remote_address = address
        self.family = family
        self.authkey = authkey

    def commit(self, method_name: str, *args, **kwargs) -> Any:
        """Used to form and send the request to the BaseServer,
        then accepts the response from it.

        Args:
            method (str): A name of the method to call on the BaseServer

        Raises:
            response: The value returned by the method on the BaseServer
        """
        self.request = (method_name, args, kwargs)

        with self.accept() as conn:
            conn.send(self.request)

        self.response, self.session_socket = recv_from(
            self.remote_address, self.family, self.authkey
        )

        if isinstance(self.response, (NotImplementedError, ValueError)):
            raise self.response

        super().__init__(address=self.session_socket)

        return self.response


class Session:
    """A context manager for Client. Supports multiple requests per session."""

    def __init__(
        self,
        server_address: Tuple[str, int],
        family: str = None,
        authkey: bytes = None,
    ) -> None:
        self.client = _Client(address=server_address, family=family, authkey=authkey)

    def __enter__(self) -> _Client:
        return self.client

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if not __exc_type:
            self.client.commit(method_name=SIGENDSESSION)
            self.client.close()
            if self.client.response != SIGENDSESSION:
                raise ValueError(f"Improperly closed session: {self.client.response}")
