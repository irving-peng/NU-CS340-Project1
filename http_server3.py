import socket
import sys
import os
import json
from urllib.parse import urlparse, parse_qs

def get_request(connection):
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        d = connection.recv(1024) #keep reading until blank
        if not d:
            break
        buffer += d
    
    request_line = buffer.decode('utf-8')
    
    informations = request_line.partition("\r\n\r\n")
   
    request = informations[0].split("\r\n")[0]
    header_dictionary = {}
    for l in informations[0].split("\r\n")[1:]:
        k, v = l.split(": ", 1)
        header_dictionary[k] = v
    return request, header_dictionary, informations[2]

def productRequest(string):
    parameters = parse_qs(string)
    signs = []
    for k, v in parameters.items():
        try:
            signs.append(float(v[0]))
        except ValueError:
            return None, "400 Bad Request"
    
    if not signs:
        return None, "400 Bad Request"
    
    result = 1
    for number in signs:
        result *= number

    reponse = {"operation" : "product", "operands" : signs, "result" : result }

    return json.dumps(reponse), "200 OK"


def resolve_request(connection):
    information = get_request(connection)
    print(f"Request Data: {information[0]}")
    print(f"Headers: {information[1]}")

    method, path,_ = information[0].split()

    url = urlparse(path)
    path = url.path
    query = url.query

    if method == 'GET':
        if path == "/product":
            if query:
                resp, status = productRequest(query)
                if status == "200 OK":
                    resp = ("HTTP/1.1 200 OK\r\n""Content-Type: application/json\r\n"f"Content-Length: {len(resp)}\r\n""\r\n"f"{resp}")
                    connection.sendall(resp.encode('utf-8'))
                else:
                    resp = (f"HTTP/1.1 {status} \r\n""Content-Type: text/plain\r\n"f"Content-Length: {len(status)} \r\n""\r\n"f"{status}")
                    connection.sendall(resp.encode('utf-8'))         
            else:
                resp = ("HTTP/1.1 400 Bad Request\r\n""Content-Type: text/plain\r\n""Content-Length: 13\r\n""\r\n""400 Bad Request")
                connection.sendall(resp.encode('utf-8'))
        else:
            f_p = path.lstrip('/')
            if os.path.exists(f_p):
                if f_p.endswith(('.htm', 'html')):
                    with open(f_p, 'r') as f:
                        content = f.read()
                    resp = ("HTTP/1.1 200 OK\r\n""Content-Type: text/html\r\n"f"Content-Length: {len(content)}\r\n""\r\n"f"{content}")
                    connection.sendall(resp.encode('utf-8'))
                else:
                    resp = ("HTTP/1.1 403 Forbidden\r\n""Content-Type: text/plain\r\n""Content-Length: 15\r\n""\r\n""403 Forbidden")
                    connection.sendall(resp.encode('utf-8'))         
            else:
                resp = ("HTTP/1.1 404 Not Found\r\n""Content-Type: text/plain\r\n""Content-Length: 13\r\n""\r\n""404 Not Found")
                connection.sendall(resp.encode('utf-8'))
    else:
        resp = ("HTTP/1.1 405 Method Not Allowed\r\n""Content-Type: text/plain\r\n""Content-Length: 23\r\n""\r\n""405 Method Not Allowed")
        connection.sendall(resp.encode('utf-8'))



if len(sys.argv) != 2:
    print(f"Uses: {sys.argv[0]} <port>")
    sys.exit(1)
port = int(sys.argv[1])
sockket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serAddress = ('', port)
sockket.bind(serAddress)
sockket.listen(5)
print(f"Listening on port {port}...")
while (1==1):
    conn, cliAddress = sockket.accept()
    try:
        print(f"Connecting with {cliAddress}")
        resolve_request(conn)
    finally:
        conn.close()