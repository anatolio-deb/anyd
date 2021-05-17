from sockets_framework import BaseServer


class Server(BaseServer):
    def echo(self, arg):
        return arg


if __name__ == "__main__":
    Server(("localhost", 3000)).start()
