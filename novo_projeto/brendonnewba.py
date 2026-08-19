from http.server import HTTPServer, BaseHTTPRequestHandler

class MeuServidor(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>Brendon Newba</h1>")

host = "localhost"
porta = 8000

servidor = HTTPServer((host, porta), MeuServidor)

print(f"Servidor rodando em http://{host}:{porta}")
servidor.serve_forever()

