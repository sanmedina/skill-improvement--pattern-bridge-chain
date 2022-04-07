from http.server import BaseHTTPRequestHandler


def hello(request_handler: BaseHTTPRequestHandler) -> None:
    request_handler.send_response(200)
    request_handler.end_headers()
    request_handler.wfile.write(b"HELLO")


def save(request_handler: BaseHTTPRequestHandler) -> None:
    request_handler.send_response(201)
    request_handler.end_headers()
    request_handler.wfile.write(b"SAVED")
