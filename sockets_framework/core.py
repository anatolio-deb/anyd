"""Socket Framework gives you an easy way to create
an IPC server with a custom functionality."""
from __future__ import annotations

import inspect
import logging
import time
from contextlib import AbstractContextManager
from multiprocessing import connection
from types import TracebackType
from typing import Any, Optional, Tuple, Type

SIGENDSESSION = b"SIGENDSESSION"
logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s] %(message)s",
    datefmt="%I:%M:%S",
    level=logging.DEBUG,
)


class BaseServer(connection.Listener):
    """Inherit form this class and define your methods:

    class MyServer(BaseServer):
        def my_echo_method(self, my_arg):
            return my_arg
    """

    def start(self) -> None:
        """Starts the server instance, listens for incoming connections, \
            handle's client's requets, calls appropriate method."""
        while True:
            logging.info("Listening at {}:{}".format(self.address[0], self.address[1]))

            with self.accept() as conn:
                logging.info(
                    "Incoming connection from {}:{}".format(
                        self.last_accepted[0], self.last_accepted[1]
                    )
                )

                conn.send(self.last_accepted)

            logging.info(
                "Entering session loop for client: {}:{}".format(
                    self.last_accepted[0], self.last_accepted[1]
                )
            )
            while True:
                try:
                    with connection.Client(address=self.last_accepted) as conn:
                        request = conn.recv()
                except ConnectionRefusedError:
                    time.sleep(0.01)
                else:
                    logging.info(
                        "Accepted request {} from {}:{}".format(
                            request, self.last_accepted[0], self.last_accepted[1]
                        )
                    )
                    if request[0] in dir(self):
                        for name, link in inspect.getmembers(
                            self, predicate=inspect.ismethod
                        ):
                            if name == request[0] and name not in dir(
                                connection.Listener
                            ):
                                response = link(*request[1], **request[2])
                                break
                            response = ValueError(
                                f"The method name {request[0]} is unacceptable, "
                                "consider renaming your method."
                            )
                    elif request[0] == SIGENDSESSION:
                        response = SIGENDSESSION
                    else:
                        response = NotImplementedError(request[0])

                    logging.info(
                        "Awaiting in-session request from {}:{}".format(
                            self.last_accepted[0], self.last_accepted[1]
                        )
                    )
                    with self.accept() as conn:
                        logging.info(
                            "Sending response: {} to {}:{}".format(
                                response,
                                self.last_accepted[0],
                                self.last_accepted[1],
                            )
                        )
                        conn.send((response, self.last_accepted))
                    if response == SIGENDSESSION:
                        logging.info(
                            "Ending session for {}:{}".format(
                                self.last_accepted[0], self.last_accepted[1]
                            )
                        )
                        break


class Client(connection.Listener):
    """Used with BaseServer instances. Gets communication address from the BaseServer,
    Sends a request to the BaseServer's listening address, then opens a listener on
    the received address to accept the response from the BaseServer"""

    def __init__(
        self,
        address: Type[Tuple[str, int]],
        family: str = None,
        authkey: bytes = None,
    ) -> None:
        with connection.Client(address, family, authkey) as conn:
            local_address = conn.recv()
        super().__init__(local_address)
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
        request = (method_name, args, kwargs)

        with self.accept() as conn:
            conn.send(request)
        with connection.Client(self.remote_address, self.family, self.authkey) as conn:
            response, local_address = conn.recv()
        super().__init__(local_address)
        if isinstance(response, (NotImplementedError, ValueError)):
            raise response
        return response


class Session(AbstractContextManager):
    """A context manager for Client. Supports multiple requests per session."""

    def __init__(
        self,
        server_address: Type[Tuple[str, int]],
        family: str = None,
        authkey: bytes = None,
    ) -> None:
        self.client = Client(address=server_address, family=family, authkey=authkey)

    def __enter__(self) -> Client:
        return self.client

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        response = self.client.commit(method_name=SIGENDSESSION)
        self.client.close()
        if response != SIGENDSESSION:
            raise ValueError(f"Improperly closed session: {response}")
