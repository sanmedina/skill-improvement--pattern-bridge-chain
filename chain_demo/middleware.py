import base64
from abc import ABCMeta, abstractmethod
from http.server import BaseHTTPRequestHandler
from typing import Dict, Optional, Tuple

from common import Endpoint


class MiddlewareHandler(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._next_handler: Optional["MiddlewareHandler"] = None

    def then(self, next_handler: "MiddlewareHandler") -> None:
        self._next_handler = next_handler

    @abstractmethod
    def handle(self, request_handler: BaseHTTPRequestHandler) -> None:
        ...

    def next(self, request_handler: BaseHTTPRequestHandler) -> None:
        if not self._next_handler:
            raise Exception("No next handler")
        self._next_handler.handle(request_handler)


class RouterHandler(MiddlewareHandler):
    def __init__(self) -> None:
        super().__init__()
        self._routes: Dict[Tuple[str, str], Endpoint] = {}

    def handle(self, request_handler: BaseHTTPRequestHandler) -> None:
        endpoint = self._routes.get((request_handler.command, request_handler.path))
        if endpoint:
            return endpoint(request_handler)
        self._send_not_found(request_handler)

    def add_endpoint(self, command: str, path: str, endpoint: Endpoint) -> None:
        self._routes[(command, path)] = endpoint

    def _send_not_found(self, request_handler):
        request_handler.send_response(404)
        request_handler.end_headers()
        request_handler.wfile.write(b"NOT FOUND")


class DummyHandler(MiddlewareHandler):
    def handle(self, request_handler: BaseHTTPRequestHandler) -> None:
        print(f"Got this request: {request_handler.path}")
        self.next(request_handler)


class AuthHandler(MiddlewareHandler):
    def handle(self, request_handler: BaseHTTPRequestHandler) -> None:
        basic_auth: str = request_handler.headers.get("Authorization")
        if not (basic_auth and basic_auth.startswith("Basic ")):
            request_handler.send_response(401)
            request_handler.end_headers()
            request_handler.wfile.write(b"CREDENTIALS NOT PROVIDED")
            return
        _, request_b64 = basic_auth.split(" ")
        expected_b64 = base64.b64encode(b"user:1234").decode()
        if request_b64 != expected_b64:
            request_handler.send_response(401)
            request_handler.end_headers()
            request_handler.wfile.write(b"WRONG CREDENTIALS")
            return
        self.next(request_handler)


class CacheHandler(MiddlewareHandler):
    def __init__(self) -> None:
        super().__init__()
        self._cache = set()

    def handle(self, request_handler: BaseHTTPRequestHandler) -> None:
        if request_handler.command != "GET":
            return self.next(request_handler)
        if request_handler.path in self._cache:
            request_handler.send_response(200)
            request_handler.end_headers()
            request_handler.wfile.write(b"USING CACHE")
            return
        self._cache.add(request_handler.path)
        self.next(request_handler)
