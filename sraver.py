import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", 8000))


class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


with socketserver.TCPServer(("0.0.0.0", PORT), HealthHandler) as httpd:
    httpd.serve_forever()
