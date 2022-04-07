from http.server import CGIHTTPRequestHandler
from socketserver import TCPServer

from endpoints import hello, save
from middleware import (AuthHandler, CacheHandler, DummyHandler,
                        MiddlewareHandler, RouterHandler)


class Application:
    def __init__(self) -> None:
        router = RouterHandler()
        self._register_routes(router)
        self.middleware = self._create_middleware(router)

    def _register_routes(self, router: RouterHandler):
        router.add_endpoint("GET", "/hello", hello)
        router.add_endpoint("POST", "/save", save)

    def _create_middleware(self, router: RouterHandler) -> MiddlewareHandler:
        dummy_handler = DummyHandler()
        auth_handler = AuthHandler()
        cache_handler = CacheHandler()

        dummy_handler.then(auth_handler)
        auth_handler.then(cache_handler)
        cache_handler.then(router)

        return dummy_handler

    def handler(self) -> CGIHTTPRequestHandler:
        class Handler(CGIHTTPRequestHandler):
            app = self

            def do_GET(self) -> None:
                self.app.middleware.handle(self)

            def do_POST(self) -> None:
                self.app.middleware.handle(self)

        return Handler


def main():
    app = Application()
    with TCPServer(("", 8080), app.handler()) as httpd:
        print("Serving at port 8080")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
