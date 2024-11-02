import socket 
import sys
import os
import select
# reading HTTP requests header
def get_request(connection):
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        d = connection.recv(1024) # read in a trunk of 1024 byte
        if not d:
            break
        buffer += d
    # buffer the headers and request line
    request_line = buffer.decode('utf-8')
    informations = request_line.partition("\r\n\r\n")
    request = informations[0].split("\r\n")[0]
    header_dictionary = {}
    for l in informations[0].split("\r\n")[1:]:
        k, v = l.split(": ", 1)
        header_dictionary[k] = v
    return request, header_dictionary, informations[2]
# process HTTP request
def resolve_request(connection):
    information = get_request(connection) # parse the header
    print(f"Request Data: {information[0]}")
    print(f"Headers: {information[1]}")
    method, path,_ = information[0].split() # parse requested files
    # checking all the traffics for GET request
    if method == 'GET':
        f_p = path.lstrip('/')
        if os.path.exists(f_p):
            if f_p.endswith(('.htm', 'html')):
                with open(f_p, 'r') as f:
                    content = f.read()
                # success founded file and matched the allowed file type
                resp = ("HTTP/1.1 200 OK\r\n""Content-Type: text/html\r\n"f"Content-Length: {len(content)}\r\n""\r\n"f"{content}")
                connection.sendall(resp.encode('utf-8'))
            else:
                # file existed but does not matched the allowed file type
                resp = ("HTTP/1.1 403 Forbidden\r\n""Content-Type: text/plain\r\n""Content-Length: 15\r\n""\r\n""403 Forbidden")
                connection.sendall(resp.encode('utf-8'))         
        else:
            # file not found
            resp = ("HTTP/1.1 404 Not Found\r\n""Content-Type: text/plain\r\n""Content-Length: 13\r\n""\r\n""404 Not Found")
            connection.sendall(resp.encode('utf-8'))
    else:
        # file not allowed
        resp = ("HTTP/1.1 405 Method Not Allowed\r\n""Content-Type: text/plain\r\n""Content-Length: 23\r\n""\r\n""405 Method Not Allowed")
        connection.sendall(resp.encode('utf-8'))
if len(sys.argv) != 2:
    # check if port number exist in the command
    print(f"Uses: {sys.argv[0]} <port>")
    sys.exit(1)
port = int(sys.argv[1]) 
sockket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating socket
serAddress = ('', port) # allowed all ip address
sockket.bind(serAddress)
sockket.listen(5) # wait for connections
print(f"Listening on port {port}...")
connections = []
# loop and waiting for new requests
while True:
    req_list = [sockket] + connections  # add socket to the all connections
    waiting_sockets = select.select(req_list, [], [])[0]
    for s in waiting_sockets:
        if s is sockket:
            # add new connection
            conn, cliAddress = sockket.accept()
            print(f"Connected with {cliAddress}")
            connections.append(conn)
        else:
            try:
                resolve_request(s)
            except Exception as e:
                print(f"Error with request: {e}")
            finally:
                s.close()
                connections.remove(s) # remove the connetion that is finished
