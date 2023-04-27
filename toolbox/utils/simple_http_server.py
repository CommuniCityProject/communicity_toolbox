from typing import Union
from http.server import BaseHTTPRequestHandler, HTTPServer



def create_http_server(port: int, get_callback: Union[callable, None] = None,
    post_callback: Union[callable, None] = None):
    """Run a basic https server that calls a callback every time a get or 
    post request is received. Runs forever and blocks the execution until
    a KeyboardInterrupt exception occurs.

    Args:
        port (int): The server port.
        get_callback (Union[callable, None]): Function to call when a GET
          petition is received. It must accept one argument: the path. And
          return a string with the response.
        post_callback (Union[callable, None]): Function to call when a POST
          petition is received. It must accept three parameters: The path,
          the content-type and the content data. And return a string with the
          response.
    """
    
    class CustomHTTPHandler(BaseHTTPRequestHandler):
        def _response(self, status: int, msg: str):
            self.send_response(status)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(msg.encode())

        def do_POST(self):
            length = int(self.headers["Content-Length"])
            content = self.rfile.read(length)
            if post_callback is not None:
                msg = post_callback(
                    self.path,
                    self.headers.get("Content-Type"),
                    content
                )
            else:
                msg = ""
            self._response(200, msg)

        def do_GET(self):
            msg = get_callback(self.path) if get_callback is not None \
                else ""
            self._response(200, msg)
    
    httpd = HTTPServer(("0.0.0.0", port), CustomHTTPHandler)
    httpd.allow_reuse_address = True
    try:
        print(f"Listening on port {port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
