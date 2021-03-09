# Sockets Framework

Sockets Framework will help you to implement an IPC server with your own functionality. It will also provide you with a ready-to-use client to query your server and getting responses from it.

Start a new server project from the shell:

```
sockets-framework new my_server
```

This will create a structure of a new project inside of `my_server` folder:

```bash
.
├── my_server
│   ├── core.py
│   └── __init__.py
└── settings.py
```

The `core` module is where you define your server's functions, for example:

```python
def hello(arg: str):
    return " ".join(["hello", arg])
```

Then you can start your server from the shell:

```bash
sockets-framework startserver
```

Finally, you can query your server using a `Client`:

```bash
from sockets-framework.core import Client

with Client() as call:
    response = call.commit("hello", "world")
print(response) # "hello world"
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