# Sockets Framework

Sockets Framework will help you to implement an IPC server with your own functionality. It will also provide you with a ready-to-use client to query your server and getting responses from it.

Define your server using `BaseServer`:

```python
from sockets_framework import BaseServer

class MyServer(BaseServer):
    hello = 'Hello'

    def hello(self, arg):
        return ''.join([self.hello, arg])
```

Start it:

```python
address = ('localhost', 4000)
server = MyServer(address)
server.start()
```

You can query your server using a `Client` from another environment with `sockets-framework` installed:

```python
from sockets_framework import Session

address = ('localhost', 4000)

with Session(address) as client:
    response = client.commit("hello", arg="world")
    another_response = client.commit("hello", "Bob")
print(response) # Hello world
print(another_response) # Hello Bob
```

# Features

- Get to your server's functionality implementation instantly
- Don't bother with a low-level sockets programming
- The client for your server comes out of the box and is ready to use

# Installation

Install Sockets Framework by running:

```
pip install sockets-framework
```

# Contribute

- Issue Tracker: [github.com/anatolio-deb/sockets-framework/issues](https://github.com/anatolio-deb/sockets-framework/issues)
- Source Code: [github.com/anatolio-deb/sockets-framework](https://github.com/anatolio-deb/sockets-framework)

# Support

If you are having issues, please let us know.
We have a mailing list located at [sockets-framework@googlegroups.com](mailto:sockets-framework@googlegroups.com)

# License

The project is licensed under the BSD license.
