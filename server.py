import os
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('get request')

        if self.path == '/':
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
                    w.write(f"{lgn} {pwd} 0 {'0'*1525}\n")
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
        elif data['command'] == 'verify':
            lgn, pwd = data['username'], data['password']
            wrd = data['word'] + '\n'
            if lgn in pwds and pwds[lgn] == pwd:
                if wrd in words:
                    answer['status'] = "YES"
                    if info[lgn]['guessed'][words.index(wrd)] == '0':
                        info[lgn]['quessed'][words.index(wrd)] = '1'
                        info[lgn]['integer'] += 1
                        w = open('Users.txt', 'w')
                        for lgn in info:
                            print(lgn, pwds[lgn], info[lgn]['integer'], info[lgn]['guessed'], file=w)
                        w.close()
                        answer['message'] = "This word is exists and not guessed."
                    else:
                        answer['message'] = "This word is exists, but already guessed."
                else:
                    answer['status'] = "NO"
                    answer['message'] = "This word isn't exists."
            else:
                answer['status'] = 'FAILED'
                answer['message'] = 'Invalid username or password'

        response = json.dumps(answer).encode("utf-8")
        self._set_headers()
        self.wfile.write(response)

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()


def run(handler_class=BaseHTTPRequestHandler):
    PORT = os.environ.get('PORT', "8080")
    server_address = ('', int(PORT))
    httpd = HTTPServer(server_address, handler_class)
    httpd.serve_forever()


try:
    open('Users.txt')
except FileNotFoundError:
    open('Users.txt', 'w')

wFile = open('Words.txt')
words = wFile.readlines()

wFile.close()
f = open("Users.txt")
pwds: dict = {}
info: dict = {}
for line in f:
    try:
        s = line.split()
        pwds[s[0]] = s[1]
        info[s[0]] = {'integer': s[2], 'guessed': list(s[3])}
    except IndexError:
        pass
f.close()

run(handler_class=HttpGetHandler)
