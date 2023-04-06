from collections import namedtuple

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from .constants import HTTP_1_0, HTTP_1_1, METHODS, NEWLINE
from .helpers import readuntil
from .request import HTTPRequest, Request
from .response import ResponseMaker, ResponseStream
from .routing import RouteGroup

HandlerContext = namedtuple("HandlerContext", ("request", "response"))


class HTTPServer(RouteGroup):
    """
    The HTTP/1.1 async server, with an internal RouteGroup
    """
    def __init__(
            self,
            host="127.0.0.1",
            port=8000,
            timeout=5,
            keep_alive_timeout=25,
            request_handler=Request,
            response_maker=ResponseMaker,
        ):
        super().__init__()
        self._host = host
        self._port = port
        self._timeout = timeout
        self._keep_alive_timeout = keep_alive_timeout
        self._request_handler = request_handler
        self._response_maker = response_maker

    async def _read_headers(self, reader, proto_ver):
        headers = {}

        # set default connection header based on protocol version
        # may be overridden by client headers later
        if proto_ver == HTTP_1_0:
            headers["Connection"] = "close"
        else:
            headers["Connection"] = "keep-alive"

        while (line := await asyncio.wait_for(readuntil(reader, NEWLINE), self._timeout)) != NEWLINE:
            line = line.strip(NEWLINE).decode()
            sep_i = line.find(":")
            headers[line[0:sep_i]] = line[sep_i+2:]
        return headers

    async def _read_message(self, reader):
        start_line = await asyncio.wait_for(
            readuntil(reader, NEWLINE),
            self._keep_alive_timeout or self._timeout,
        )
        start_line = start_line.strip(NEWLINE).decode()
        method, path, proto_ver = start_line.split(" ", 3)
        headers = await self._read_headers(reader, proto_ver)
        request_payload = None
        if (request_payload_length := int(headers.get("Content-Length", "0"))) != 0:
            request_payload = await asyncio.wait_for(
                reader.readexactly(request_payload_length), self._timeout)
        return HTTPRequest(proto_ver, method, path, headers, request_payload)

    async def _write_message(self, writer, response):
        raw_message = (f"{response.proto} {response.status_code}").encode() + NEWLINE
        for key, value in response.headers.items():
            raw_message += (key.encode() + b": " + value.encode() + NEWLINE)
        raw_message += NEWLINE

        if isinstance(response.payload, ResponseStream):
            # chunked payload
            writer.write(raw_message)
            await writer.drain()
            for chunk in response.payload.read():
                writer.write(chunk)
                await writer.drain()
            return
        elif response.payload:
            # normal payload
            raw_message += response.payload

        writer.write(raw_message)
        await writer.drain()

    async def _handle_conn(self, reader, writer):
        keep_alive = True
        peer_name = writer.get_extra_info("peername")
        print(f"new conn from {peer_name}")
        try:
            while keep_alive:
                http_request = await self._read_message(reader)
                print(http_request)

                # validate proto version, we don't want something unexpected
                if http_request.proto not in (HTTP_1_0, HTTP_1_1):
                    raise ValueError(f"invalid proto '{http_request.proto}' received from {peer_name}")

                if http_request.method not in METHODS:
                    raise ValueError(f"invalid method '{http_request.method}' received from {peer_name}")

                request = self._request_handler(http_request)

                # support keep-alive and close connections
                if request.headers["Connection"].lower() == "close":
                    keep_alive = False

                handler = self.get_route_handler(request.path, request.method)

                response_maker = self._response_maker(
                    http_request.proto,
                    {
                        "Connection": "keep-alive" if keep_alive else "close",
                    },
                )

                if not handler:
                    response = response_maker.html(404, "<h1>Page Not Found</h1>")
                    await self._write_message(writer, response)
                    return

                response = handler(HandlerContext(request, response_maker))
                await self._write_message(writer, response)

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
