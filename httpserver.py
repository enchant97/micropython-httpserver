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


async def readuntil(reader, separator):
    buffer = b""
    while (char := await reader.read(1)):
        buffer += char
        if buffer.endswith(separator):
            break
    return buffer


class HTTPMessage:
    def __init__(self, method, path, headers):
        self.method = method
        self.path, self.query = self._process_path(path)
        self.headers = headers

    @staticmethod
    def _process_path(path):
        query = {}
        path_split = path.split("?")
        if len(path_split) > 1:
            path, query_string = path_split
            query_string = query_string.split("&")
            query_string = map(lambda v:v.split("="), query_string)
            for key, value in query_string:
                query[key] = value
        return path, query

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
    return proto_ver, HTTPMessage(method, path, headers)


async def write_message(writer, status_code, status_text, headers, payload=None):
    raw_message = (f"{HTTP_1_1} {status_code} {status_text}").encode() + NEWLINE
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

    async def _handle_conn(self, reader, writer):
        peer_name = writer.get_extra_info("peername")
        print(f"new conn from {peer_name}")
        try:
            _, message = await read_message(reader)
            print(message)

            await write_message(
                writer,
                200, "OK",
                {"Connection": "close", "Content-Length": "20"},
                b"<h1>Hello World</h1>",
            )

            writer.close()
            await writer.wait_closed()
        finally:
            print(f"conn closed from {peer_name}")

    async def start(self):
        print(f"listening on: {self._host}:{self._port}")
        self._server = await asyncio.start_server(
            self._handle_conn,
            host=self._host,
            port=self._port,
        )
