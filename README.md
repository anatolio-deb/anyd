# Sockets Framework

Sockets Framework will help you to implement an IPC server with your own functionality. It will also provide you with a ready-to-use client to query your server and getting responses from it.

Define your server using `BaseServer`:

```python
from sockets_framework import BaseServer

class MyServer(BaseServer):
    hello = 'Hello'
```

Use `@expose` decorator to expose your API to the client:

```python
from sockets_framework import BaseServer, expose

class MyServer(BaseServer):
    hello = 'Hello'

		@expose
    def hello(self, arg):
        return f"{self.hello} {arg}"
```

You can use any number of helper methods without decorating them:

```python
from sockets_framework import BaseServer, expose

class MyServer(BaseServer):
    hello = 'Hello'

		@expose
    def hello(self, arg):
        return self.validate_hello(arg)

		def validate_hello(self, arg: Any):
		    if not isinstance(arg, str):
				    return TypeError(arg)
				return f"{self.hello} {arg}"
```

Those methods won't expose to the client API. When API endpoint returns an exception, it will be raised on the client side.

Start `MyServer`:

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
		# you can pass keyword arguments to API request
    response = client.commit("hello", arg="world")
		# or the positional one's
    bob = client.commit("hello", "Bob")
		# you can query different API endpoints per-session
		client.commit("validate_hello", "hello") # NotImplementedError: validate_hello

print(response) # Hello world
print(bob) # Hello Bob

with Session(address) as client:
		# handling exception form the server's response
		try:
				client.commit("hello", 1) # TypeError: 1
		except TypeError:
				print("We are not greeting anyone but strings!")
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