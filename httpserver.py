try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

NEWLINE = b"\r\n"
HTTP_1_1 = "HTTP/1.1"

# Default values given by client
DEFAULT_CLIENT_HEADERS = {
    "Connection": "keep-alive",
}


def perc_decode(v, from_form=False):
    decoded = b""
    i = 0
    while i < len(v):
        if v[i] == "%":
            encoded = v[i+1:i+3]
            decoded += bytes.fromhex(encoded)
            i += 2
        elif from_form and v[i] == "+":
            decoded += b" "
        else:
            decoded += v[i].encode()
        i += 1
    return decoded


async def readuntil(reader, separator):
    buffer = b""
    while (char := await reader.read(1)):
        buffer += char
        if buffer.endswith(separator):
            break
    return buffer


def process_query_string(query_string):
    query = {}
    query_string = query_string.split("&")
    query_string = map(lambda v:v.split("="), query_string)
    for key, value in query_string:
        query[key] = value
    return query


class HTTPMessage:
    def __init__(self, method, path, headers, payload):
        # "GET"
        self.method = method.upper()
        # "/" {"name": "value", ...}
        self.path, self.query = self._process_path(path)
        # {"name": "value", ...}
        self.headers = headers
        self.payload = payload

    @staticmethod
    def _process_path(path):
        query = {}
        path_split = path.split("?")
        if len(path_split) > 1:
            path, query_string = path_split
            query = process_query_string(query_string)
        return path, query

    @property
    def form(self):
        if self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            return process_query_string(self.payload.decode())
        raise ValueError("not valid form")

    def __repr__(self) -> str:
        return f"{self.method}\n{self.path} {self.query}\n{self.headers}"


async def get_headers(reader):
    headers = DEFAULT_CLIENT_HEADERS.copy()
    while (line := await readuntil(reader, NEWLINE)) != NEWLINE:
        line = line.strip(NEWLINE).decode()
        sep_i = line.find(":")
        headers[line[0:sep_i]] = line[sep_i+2:]
    return headers


async def read_message(reader):
    start_line = (await readuntil(reader, NEWLINE)).strip(NEWLINE)
    method, path, proto_ver = start_line.decode().split(" ")
    headers = await get_headers(reader)
    request_payload = None
    if (request_payload_length := int(headers.get("Content-Length", "0"))) != 0:
        request_payload = await reader.readexactly(request_payload_length)
    return proto_ver, HTTPMessage(method, path, headers, request_payload)


async def write_message(writer, status_code, headers, payload=None):
    raw_message = (f"{HTTP_1_1} {status_code}").encode() + NEWLINE
    for key, value in headers.items():
        raw_message += (key.encode() + b": " + value.encode() + NEWLINE)
    raw_message += NEWLINE
    if payload:
        raw_message += payload
    writer.write(raw_message)
    await writer.drain()


class HTTPServer:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        # {("/", "GET"): func, ... }
        self._routes = {}

    async def _handle_conn(self, reader, writer):
        peer_name = writer.get_extra_info("peername")
        print(f"new conn from {peer_name}")
        try:
            _, message = await read_message(reader)
            print(message)

            handler = self._routes.get((message.path, message.method))

            if not handler:
                await write_message(
                    writer,
                    404,
                    {"Connection": "close", "Content-Length": "23"},
                    b"<h1>Page Not Found</h1>",
                )
                return

            status_code, headers, payload = handler(message)
            payload_length = len(payload)
            headers["Connection"] = "close"
            headers["Content-Length"] = str(payload_length)

            await write_message(
                writer,
                status_code,
                headers,
                payload,
            )

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

    def route(self, path, method="GET"):
        def decorator(fn):
            self._routes[(path, method.upper())] = fn
        return decorator
