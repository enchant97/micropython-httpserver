import json
from collections import namedtuple

from .constants import NEWLINE, HTTP_1_1

# (int, dict[str, str], bytes | ResponseStream | None)
HTTPResponse = namedtuple("HTTPResponse", ("proto", "status_code", "headers", "payload"))


def create_chunk(data):
    return (
        format(len(data), "x").encode("ascii") +
        NEWLINE +
        data +
        NEWLINE
    )


class ResponseStream:
    def __init__(self, stream) -> None:
        self._stream = stream

    def read(self):
        for chunk in self._stream:
            yield create_chunk(chunk)
        # EOF
        yield create_chunk(b"")


class ResponseMaker:
    def __init__(self, proto, headers) -> None:
        self._proto = proto
        # type: (dict[str, str]) -> (dict[str, str])
        self._headers = headers

    def get_header(self, key):
        return self._headers.get(key)

    def set_header(self, key, value):
        self._headers[key] = value

    def no_content(self, status_code):
        return HTTPResponse(self._proto, status_code, self._headers, None)

    def content(self, status_code, content_type, content):
        self._headers["Content-Type"] = content_type
        self._headers["Content-Length"] = str(len(content))
        return HTTPResponse(self._proto, status_code, self._headers, content)

    def content_stream(self, status_code, content_type, stream):
        if self._proto != HTTP_1_1:
            raise ValueError("client does not support 'chunked' encoding")
        self._headers["Content-Type"] = content_type
        self._headers["Transfer-Encoding"] = "chunked"
        if not isinstance(stream, ResponseStream):
            stream = ResponseStream(stream)
        return HTTPResponse(self._proto, status_code, self._headers, stream)

    def text(self, status_code, text):
        return self.content(status_code, "text/plain", text.encode())

    def html(self, status_code, html):
        return self.content(status_code, "text/html", html.encode())

    def json(self, status_code, obj):
        data = json.dumps(obj).encode()
        return self.content(status_code, "application/json", data)

    def file(self, path, content_type="application/octet-stream"):
        def stream():
            with open(path, "rb") as fo:
                for chunk in fo:
                    yield chunk
        return self.content_stream(200, content_type, stream())

    def redirect(self, status_code, url):
        if status_code < 300 or status_code >= 400:
            raise ValueError("invalid status code given for redirect must be 300-399")
        self._headers["Location"] = url
        return self.no_content(status_code)
