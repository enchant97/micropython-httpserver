import json
from collections import namedtuple

HTTPRequest = namedtuple("HTTPRequest", ("proto", "method", "path", "headers", "payload"))


def process_query_string(query_string):
    query = {}
    query_string = query_string.split("&")
    query_string = map(lambda v:v.split("="), query_string)
    for key, value in query_string:
        query[key] = value
    return query


def process_path(path):
    query = {}
    path_split = path.split("?")
    if len(path_split) > 1:
        path, query_string = path_split
        query = process_query_string(query_string)
    return path, query


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
