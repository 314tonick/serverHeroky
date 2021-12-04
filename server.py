from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        for name in dir(self):
            if not name.startswith('_'):
                print(name, self.__getattribute__(name))
        print('get request')

        self._set_headers()
        self.wfile.write('<!doctype html>'.encode())
        self.wfile.write('<html><head><meta charset="utf-8">'.encode())
        self.wfile.write('<title>LocalServer.</title></head>'.encode())
        self.wfile.write('<body>Hello world!</body></html>'.encode())

    def do_POST(self):
        answer: dict = {}
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        print(f"Received data: {data}")
        if data['command'] == 'login':
            lgn, pwd = data['username'], data['password']
            if lgn in pwds:
                if pwd == pwds[lgn]:
                    answer['signed_in'] = "OK"
                    answer['message'] = "Login! :)"
                else:
                    answer['signed_in'] = "Failed"
                    answer['message'] = "Wrong password :("
            else:
                answer['signed_in'] = "Failed"
                answer['message'] = "Username is not found :("
        elif data['command'] == 'register':
            lgn, pwd = data['username'], data['password']
            if lgn in pwds:
                answer['registered'] = "Failed"
                answer['message'] = "This username is already taken! :("
            else:
                answer['signed_in'] = "OK"
                answer['message'] = "Registered! :)"
                pwds[lgn] = pwd
                with open("Users.txt", "a") as w:
                    w.write(f"{lgn} {pwd}\n")
        elif data['command'] == 'get':
            lgn, pwd = data['username'], data['password']
            parameter = data['parameter']
            if lgn in pwds:
                if pwd == pwds[lgn]:
                    if parameter in info[lgn]:
                        answer['status'] = "OK"
                        answer['message'] = "Correct! :)"
                        answer['result'] = int(info[lgn])
                    else:
                        answer['status'] = "Failed"
                        answer['message'] = "Invalid parameter :("
                else:
                    answer['status'] = "Failed"
                    answer['message'] = "Wrong password :("
            else:
                answer['status'] = "Failed"
                answer['message'] = "Username is not found :("

        response = json.dumps(answer).encode("utf-8")
        self._set_headers()
        self.wfile.write(response)

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()


def run(handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, handler_class)
    httpd.serve_forever()


try:
    open('Users.txt')
except FileNotFoundError:
    open('Users.txt', 'w')

f = open("Users.txt")
pwds: dict = {}
info: dict = {}
for line in f:
    s = line.split()
    pwds[s[0]] = s[1]
    info[s[0]] = {'integer': s[2]}
f.close()

run(handler_class=HttpGetHandler)
