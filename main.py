import mimetypes
import pathlib
import socket
import urllib.parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep
from datetime import datetime


class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/":
            self.send_html_file("index.html")
        elif parsed_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(parsed_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html")

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        run_client(IP, UDP_PORT, data)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler):
    server_address = (IP, MAIN_SERVER_PORT)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv = ip, port
    sock.bind(serv)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            final_dict = {str(datetime.now()): data_dict}
            write_to_json(PATH, final_dict)
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def run_client(ip, port, all_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv = ip, port
    sock.sendto(all_data, serv)
    sock.close()


def write_to_json(path, data):
    with open(path, "r") as outfile:
        file_data = json.loads(outfile.read())
        file_data.update(data)
    with open(path, "w") as outfile:
        json.dump(file_data, outfile)


if __name__ == '__main__':

    PATH = "storage/data.json"
    IP = "127.0.0.1"
    MAIN_SERVER_PORT = 3000
    UDP_PORT = 5000

    main_server = Thread(target=run)
    server = Thread(target=run_server, args=(IP, UDP_PORT))

    main_server.start()
    server.start()
    print('All started!')


