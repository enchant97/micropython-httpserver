from collections import namedtuple

# (int, dict[str, str], bytes | None)
HTTPResponse = namedtuple("HTTPResponse", ("status_code", "headers", "payload"))


class ResponseMaker:
    def __init__(self, headers) -> None:
        # type: (dict[str, str]) -> (dict[str, str])
        self._headers = headers

    def no_content(self, status_code):
        return HTTPResponse(status_code, self._headers, None)

    def content(self, status_code, content_type, content):
        self._headers.setdefault("Content-Type", content_type)
        self._headers["Content-Length"] = str(len(content))
        return HTTPResponse(status_code, self._headers, content)

    def text(self, status_code, text):
        return self.content(status_code, "text/plain", text.encode())

    def html(self, status_code, html):
        return self.content(status_code, "text/html", html.encode())

    def redirect(self, status_code, url):
        if status_code < 300 or status_code >= 400:
            raise ValueError("invalid status code given for redirect must be 300-399")
        self._headers["Location"] = url
        return self.no_content(status_code)
