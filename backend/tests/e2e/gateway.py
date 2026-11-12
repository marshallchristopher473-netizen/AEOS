"""Local stand-in for the Supabase URL layout.

  GET  /auth/v1/jwks   -> static JWKS (public half of the local RSA test key)
  *    /rest/v1/<path> -> forwarded verbatim to PostgREST

Only path routing is emulated. Authorization is NOT emulated: PostgREST and
PostgreSQL make every decision, exactly as in Supabase."""
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1])
UPSTREAM = sys.argv[2]
JWKS = open(sys.argv[3], "rb").read()
HOP = {"connection", "keep-alive", "transfer-encoding", "host", "content-length"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _send(self, code, headers, body):
        self.send_response(code)
        for k, v in headers:
            if k.lower() not in HOP:
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self):
        if self.path == "/auth/v1/jwks":
            return self._send(200, [("Content-Type", "application/json")], JWKS)
        if not self.path.startswith("/rest/v1/"):
            return self._send(404, [], b"not found")
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(
            UPSTREAM + self.path[len("/rest/v1"):],
            data=body,
            method=self.command,
            headers={k: v for k, v in self.headers.items() if k.lower() not in HOP},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                self._send(resp.status, resp.getheaders(), resp.read())
        except urllib.error.HTTPError as err:
            self._send(err.code, err.headers.items(), err.read())

    do_GET = do_POST = do_PATCH = do_DELETE = do_HEAD = _handle


ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
