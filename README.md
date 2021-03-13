# Sockets Framework

Sockets Framework will help you to implement an IPC server with your own functionality. It will also provide you with a ready-to-use client to query your server and getting responses from it.

Start a new server project from the shell:

```
sockets-framework new my_server
```

This will create a new `my_server` folder with a structure of a new project:

```bash
.
├── core
│   ├── __init__.py
│   ├── my_server.py
│   └── settings.py
└── manage.py
```

`my_server` module is where you define your server's functions, for example:

```python
def hello(arg: str):
    return " ".join(["hello", arg])
```

Then you can start your server from the shell:

```bash
python manage.py startserver
```

Finally, you can query your server using a `Client` from another environment with a `sockets-framework` installed:

```python
from sockets_framework.core import Client

server_address = ("localhost", 3000)

with Client(server_address) as session:
    response = session.commit("hello", "world")
    another_response = session.commit("hello", "Bob")
print(response) # hello world
print(another_response) # hello Bob
```

# Features

- Get to your server's functionality implementation instantly
- Don't bother with a low-level sockets programming
- Get a nice structured project from the beginning
- The client for your server comes out-of-the-box

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

The project is licensed under the MIT license.
