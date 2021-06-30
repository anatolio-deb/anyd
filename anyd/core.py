from __future__ import annotations

import logging
import time
from multiprocessing.connection import Client, Listener
from types import FunctionType, TracebackType
from typing import Any, Iterable, Optional, Tuple, Type

logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    # datefmt="%m/%d/%Y:%I:%M:%S",
    level=logging.INFO,
)
SIGENDSESSION: bytes = b"SIGENDSESSION"


def _recv_from(*args, **kwargs):
    with Client(*args, **kwargs) as conn:
        return conn.recv()


class Appd(Listener):
    """Inherit form this class and define your methods:

    class MyServer(Appd):
        def my_echo_method(self, my_arg):
            return my_arg
    """

    response: Any = None
    request: Tuple[str][Iterable] = ()
    _api: dict = {}

    def api(self, func: FunctionType):
        self._api[func.__name__] = func

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

                conn.send((self.response, self.last_accepted))
            while self.response != SIGENDSESSION and not isinstance(
                self.response, (NotImplementedError, ValueError)
            ):
                logging.info(
                    "Session loop started for client: %s:%s",
                    self.last_accepted[0],
                    self.last_accepted[1],
                )

                while True:
                    try:
                        self.request = _recv_from(address=self.last_accepted)
                    except ConnectionRefusedError as ex:
                        logging.error(ex)
                    else:
                        break
                    finally:
                        time.sleep(1)

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

                self.request = None

            self.response = None

            logging.info(
                "Ending session for %s:%s",
                self.last_accepted[0],
                self.last_accepted[1],
            )

    def _set_response(self):
        if self.request[0] in self._api.keys():
            self.response = self._api[self.request[0]](
                *self.request[1], **self.request[2]
            )
        elif self.request[0] == SIGENDSESSION:
            self.response = SIGENDSESSION
        else:
            self.response = NotImplementedError(self.request[0])


class _Client(Listener):
    """Used with Appd instances. Gets communication address from the Appd,
    Sends a request to the Appd's listening address, then opens a listener on
    the received address to accept the response from the Appd"""

    response: Any = None
    request: Tuple[str][Iterable] = ()

    def __init__(
        self, address: str | Tuple[str, int], family: str | None, authkey: bytes | None
    ) -> None:
        self.response, self.session_socket = _recv_from(address, family, authkey)

        while True:
            try:
                super().__init__(address=self.session_socket)
            except OSError:
                time.sleep(2)
            else:
                break

        self.remote_address = address
        self.family = family
        self.authkey = authkey

    def commit(self, method_name: str, *args, **kwargs) -> Any:
        """Used to form and send the request to the Appd,
        then accepts the response from it.

        Args:
            method (str): A name of the method to call on the Appd

        Raises:
            response: The value returned by the method on the Appd
        """
        self.request = (method_name, args, kwargs)

        with self.accept() as conn:
            conn.send(self.request)

        self.__init__(self.remote_address, self.family, self.authkey)

        if isinstance(self.response, (NotImplementedError, ValueError)):
            raise self.response

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
            if self.client.response != SIGENDSESSION:
                raise ValueError(f"Improperly closed session: {self.client.response}")
        self.client.close()
