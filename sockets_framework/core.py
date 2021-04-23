"""[summary]

Returns:
    [type]: [description]
"""
from __future__ import annotations

import inspect
import time
from contextlib import AbstractContextManager
from multiprocessing import connection
from types import TracebackType
from typing import Any, Optional, Tuple, Type

SIGENDSESSION = b"SIGENDSESSION"


def _receive(*args, **kwargs) -> Any:
    """[summary]

    Returns:
        Any: [description]
    """
    while True:
        try:
            with connection.Client(*args, **kwargs) as conn:
                response = conn.recv()
        except ConnectionRefusedError:
            time.sleep(0.1)
        else:
            return response


class BaseServer(connection.Listener):
    """[summary]

    Args:
        BaseServer ([type]): [description]
    """

    def start(self) -> None:
        """[summary]"""
        while True:
            with self.accept() as conn:
                conn.send(self.last_accepted)
            while True:
                request = _receive(address=self.last_accepted)
                if request[0] in dir(self):
                    for name, link in inspect.getmembers(
                        self, predicate=inspect.ismethod
                    ):
                        if name == request[0] and name not in dir(connection.Listener):
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
                with connection.Listener(address=self.last_accepted) as listener:
                    with listener.accept() as conn:
                        conn.send(response)
                if response == SIGENDSESSION:
                    break


class Client(connection.Listener):
    """[summary]

    Args:
        Listener ([type]): [description]
    """

    def __init__(self, *args, **kwargs) -> None:
        self.local_address = _receive(*args, **kwargs)
        super().__init__(address=self.local_address)

    def commit(self, method_name: str, *args, **kwargs) -> Any:
        """[summary]

        Args:
            method (str): [description]

        Raises:
            response: [description]

        Returns:
            Any: [description]
        """
        request = (method_name, args, kwargs)
        with self.accept() as conn:
            conn.send(request)
        self.close()
        response = _receive(address=self.local_address)
        super().__init__(self.local_address)
        if isinstance(response, (NotImplementedError, ValueError)):
            raise response
        return response


class Session(AbstractContextManager):
    """[summary]"""

    def __init__(
        self,
        server_address: Type[str] | Type[Tuple[str, int]],
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
        self.client.commit(method_name=SIGENDSESSION)
        self.client.close()
