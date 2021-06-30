# Anyd

Anyd is a small framework that will help you build and use *any* custom Unix *daemon* process as a server. It will suite your daemon with API accessible over sockets, so you'll be able to query it for runnig your code or transmit the data. Anyd provides you a client out-of-the-box, so you can start working with your daemon instantly.

# How-to

Anyd provides you an app to start with:

```python
from anyd import Appd
```

Define the address for your daemon, for example:

```python
address = ("localhost", 3000)
```

The daemon process will use it to accept connections. Next, create a daemon app:

```python
appd = Appd(address)
```

Or you can set it up with authentication for client:

```python
appd = Appd(address, authkey=b"swordfish")
```

Now, define your API endpoints, using `@appd.api`:

```python
@appd.api
def echo(arg: str) -> str:
    return arg
```

Additionally, you can use built-in logger to log something specific:

```python
from anyd import logger

@appd.api
def echo(arg: str) -> str:
    logging.info(f"echoing: {arg}")
    return arg
```

This function is now exposed to the client as an API endpoint, and can be executed on request.

You are ready to start the deamon:

```python
appd.start()
```

That will block the interpreter and you'll see the logging output of your daemon in the terminal:

```
[INFO] Listening on 127.0.0.1:3000
```

Let's test it from another shell!

Start from importing  `Session`:

```python
from sockets_framework import Session
```

Use it with address and authkey you used for your daemon:

```python
address = ('localhost', 3000)

with Session(address, authkey=b"swordfish") as client:
    # you can pass keyword arguments to API request
    response = client.commit("echo", arg="hello world!")
    # or the positional ones
    bob = client.commit("echo", "hello Bob")
    # you can query different API endpoints per-session
    try:
        # Will raise NotImplementedError:
        # we didn't defined 'my_func' endpoint on the daemon.
        # The daemon will continue working.
        client.commit("my_func", "hello") 
    except NotImplementedError as ex:
        print(ex) # NotImplementedError: my_func

print(response) # hello world!
print(bob) # hello Bob
```

## Validators

On the daemon app you may want to define sort of validation logic for some of your endpoints. In this case, you can return an exception as a response to the client. It will be pickled and raised on the client side, so your daemon will stay up and running. Consider simple example with previous endpoit:

```python
def validate_echo(arg: Any):
    if not isinstance(arg, str):
        return TypeError(f"{arg}, {type(arg)}")
    return arg

@appd.api
def echo(arg: str) -> str:
    return validate_echo(arg)
```

The function `validate_echo` is not an API endpoint of our daemon, but still its accessible for the daemon to execute it locally.

Now, let's try to query it with wrong data:

```python
with Session(address) as client:
    try:
        client.commit("echo", 1) # will raise TypeError
    except TypeError as ex:
        print(ex) # 1, <class 'int'>
```

# Features

- Get to your server's functionality implementation instantly
- Don't bother with a low-level sockets programming
- The client for your server comes out of the box and is ready to use

# Installation

Install it by running:

```
pip install anyd
```

# Contribute

- Issue Tracker: [github.com/anatolio-deb/anyd/issues](http://github.com/anatolio-deb/anyd/issues)
- Source Code: [github.com/anatolio-deb/anyd](http://github.com/anatolio-deb/anyd)

# License

The project is licensed under the BSD license.
