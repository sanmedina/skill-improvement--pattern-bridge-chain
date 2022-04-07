from http.server import BaseHTTPRequestHandler
from typing import Callable

Endpoint = Callable[[BaseHTTPRequestHandler], None]
