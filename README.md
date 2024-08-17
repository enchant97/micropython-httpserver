# MicroPython HTTPServer
A asynchronous HTTP server & framework targeting HTTP/1.1, designed to be lightweight and easy to use.

> **WIP** not suited for use outside of testing

Although this library is built specifically for MicroPython it can run on CPython (official Python interpreter).

Read the docs [here](docs/index.md) for more info.

## Features
- HTTP/1.1 & HTTP/1.0 support
- Supports Keep-Alive connections
- Definable routes using decorators
- Route groups, for splitting routes into separate files
- Asynchronous

## Limitations
- Only has internal http server, does not support WSGI/ASGI
- Must use asyncio
- MicroPython => 1.23

## Works On
- Raspberry Pi Pico W
