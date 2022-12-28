try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from .constants import DEFAULT_CLIENT_HEADERS, NEWLINE
from .request import HTTPRequest


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


async def read_headers(reader, timeout):
    headers = DEFAULT_CLIENT_HEADERS.copy()
    while (line := await asyncio.wait_for(readuntil(reader, NEWLINE), timeout)) != NEWLINE:
        line = line.strip(NEWLINE).decode()
        sep_i = line.find(":")
        headers[line[0:sep_i]] = line[sep_i+2:]
    return headers


async def read_message(reader, timeout, keep_alive_timeout):
    start_line = await asyncio.wait_for(readuntil(reader, NEWLINE), keep_alive_timeout or timeout)
    start_line = start_line.strip(NEWLINE)
    method, path, proto_ver = start_line.decode().split(" ", 3)
    headers = await read_headers(reader, timeout)
    request_payload = None
    if (request_payload_length := int(headers.get("Content-Length", "0"))) != 0:
        request_payload = await asyncio.wait_for(
            reader.readexactly(request_payload_length), timeout)
    return HTTPRequest(proto_ver, method, path, headers, request_payload)


async def write_message(writer, response):
    raw_message = (f"{response.proto} {response.status_code}").encode() + NEWLINE
    for key, value in response.headers.items():
        raw_message += (key.encode() + b": " + value.encode() + NEWLINE)
    raw_message += NEWLINE
    if response.payload:
        raw_message += response.payload
    writer.write(raw_message)
    await writer.drain()
