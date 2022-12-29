from .constants import METHOD_GET


class RouteGroup:
    """
    Handle registering routes and registering other route groups
    """
    def __init__(self, url_prefix = "/") -> None:
        # {("/", "GET"): func, ... }
        self.routes = {}
        if not url_prefix.endswith("/"):
            url_prefix = url_prefix + "/"
        self._url_prefix = url_prefix

    def route(self, path, method=METHOD_GET):
        path = self._url_prefix + path.lstrip("/")
        def decorator(fn):
            self.routes[(path, method.upper())] = fn
        return decorator

    def get_route_handler(self, path, method):
        return self.routes.get((path, method))

    def register_route_group(self, group):
        self.routes.update(group.routes)
