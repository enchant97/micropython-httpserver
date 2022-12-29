import json
from collections import namedtuple

from .helpers import process_path, process_query_string


HTTPRequest = namedtuple("HTTPRequest", ("proto", "method", "path", "headers", "payload"))


class Request:
    def __init__(self, http_request):
        # "GET"
        self.method = http_request.method.upper()
        # "/" {"name": "value", ...}
        self.path, self.query = process_path(http_request.path)
        # {"name": "value", ...}
        self.headers = http_request.headers
        self.payload = http_request.payload

    @property
    def form(self):
        if self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            return process_query_string(self.payload.decode())
        raise ValueError("not valid form")

    def json(self, force=False):
        if (self.headers.get("Content-Type") == "application/json") or force:
            if not self.payload:
                return
            return json.loads(self.payload.decode())
        raise ValueError("not json content type")

    def __repr__(self) -> str:
        return f"{self.method}\n{self.path} {self.query}\n{self.headers}"
