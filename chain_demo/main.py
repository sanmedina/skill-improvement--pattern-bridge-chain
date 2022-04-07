from http.server import CGIHTTPRequestHandler
from socketserver import TCPServer

from endpoints import hello, save
from middleware import (AuthHandler, DummyHandler, MiddlewareHandler,
                        RouterHandler)


def create_middleware(router: RouterHandler) -> MiddlewareHandler:
    dummy_handler = DummyHandler()
    auth_handler = AuthHandler()

    dummy_handler.then(auth_handler)
    auth_handler.then(router)

    return dummy_handler


class Handler(CGIHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        router = RouterHandler()
        self._register_routes(router)
        self.middleware = create_middleware(router)
        super().__init__(*args, **kwargs)

    def _register_routes(self, router: RouterHandler):
        router.add_endpoint("GET", "/hello", hello)
        router.add_endpoint("POST", "/save", save)

    def do_GET(self) -> None:
        self.middleware.handle(self)

    def do_POST(self) -> None:
        self.middleware.handle(self)


def main():
    with TCPServer(("", 8080), Handler) as httpd:
        print("Serving at port 8080")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
