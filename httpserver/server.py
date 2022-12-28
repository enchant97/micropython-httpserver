from collections import namedtuple

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from .constants import HTTP_1_0, HTTP_1_1, METHODS
from .helpers import read_message, write_message
from .request import Request
from .response import ResponseMaker
from .routing import RouteGroup

HandlerContext = namedtuple("HandlerContext", ("request", "response"))


class HTTPServer(RouteGroup):
    """
    The HTTP/1.1 async server, with an internal RouteGroup
    """
    def __init__(self, host, port, timeout=5, keep_alive_timeout=25):
        super().__init__()
        self._host = host
        self._port = port
        self._timeout = timeout
        self._keep_alive_timeout = keep_alive_timeout

    async def _handle_conn(self, reader, writer):
        keep_alive = True
        peer_name = writer.get_extra_info("peername")
        print(f"new conn from {peer_name}")
        try:
            while keep_alive:
                http_request = await read_message(reader, self._timeout, self._keep_alive_timeout)
                print(http_request)

                # validate proto version, we don't want something unexpected
                if http_request.proto not in (HTTP_1_0, HTTP_1_1):
                    raise ValueError(f"invalid proto '{http_request.proto}' recived from {peer_name}")

                if http_request.method not in METHODS:
                    raise ValueError(f"invalid method '{http_request.method}' recived from {peer_name}")

                request = Request(http_request)

                # suport keep-alive and close connections
                if request.headers["Connection"].lower() == "close" or http_request.proto == HTTP_1_0:
                    keep_alive = False

                handler = self.get_route_handler(request.path, request.method)

                response_maker = ResponseMaker(
                    http_request.proto,
                    {
                        "Connection": "keep-alive" if keep_alive else "close",
                    },
                )

                if not handler:
                    response = response_maker.html(404, "<h1>Page Not Found</h1>")
                    await write_message(writer, response)
                    return

                response = handler(HandlerContext(request, response_maker))
                await write_message(writer, response)

        except asyncio.TimeoutError:
            print(f"connection from {peer_name} timed out")

        finally:
            writer.close()
            await writer.wait_closed()
            print(f"conn closed from {peer_name}")

    async def start(self):
        print(f"listening on: {self._host}:{self._port}")
        self._server = await asyncio.start_server(
            self._handle_conn,
            host=self._host,
            port=self._port,
        )
