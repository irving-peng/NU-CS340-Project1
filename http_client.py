import socket
import sys

def getInfo(httpLink, current_host = None) :
    firstSeven = httpLink[:7]
    if firstSeven != "http://": #check if the link with header of http://
        sys.stderr.write("The link is not in the correct format \n")
        sys.exit(1)

    httpLink = httpLink[7:]

    host = "" #create variables
    path = ""
    port = 80
    
    strings = httpLink.split("/") #split by /
    host = strings[0].strip() #get the host
    if (":" in host):
        hostParts = host.split(":") #the situation that has port
        host = hostParts[0].strip() #get host
        port = int(hostParts[1].strip()) #get port
    else:
        port = 80 #default port number
    
    if len(strings) > 1: # check if there is a path
        path = "/" + "/".join(strings[1:])
    else:
        path = "/"

    return host if host else current_host, port, path

def sendMessage(host, port, path):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #set up the socket for client
    clientSocket.settimeout(20) #set the time out

    try: # connect the server sucessfully
        clientSocket.connect((host,port))
    except socket.error: # report the connection failed error
        sys.stderr.write("Socket error: Cannot connect to host")
        sys.exit(1)
    
    message = "GET " + path + " HTTP/1.0\r\nHost: " + host + "\r\n\r\n" #the get message
    request = message.encode() #encode the message
    clientSocket.sendall(request) #send request
    return clientSocket

def receiveResponse(socket):
    message = b"" #the message to receive from the server
    while True:
        piece = socket.recv(1024) #keep receiving until the end
        if not piece:
            break
        message += piece

    
    response = message.decode() #decode
    
    return response # return response

def printBody(response,socket):
    strings = response.partition("\r\n\r\n")
    header = strings[0]
    body = strings[2]
    print(body)

    socket.close()
    return header

def redirect(header,socket , host):
    max = 10
    directNumber = 0
    while directNumber < max:
        if "301 Moved Permanently" in header or "302 Found" in header:
            directNumber += 1
            lines = header.splitlines()
            location = None
            for line in lines:
                if line.startswith("Location:"):
                    location = line.partition(":")[2].strip()
                    break
            if not location:
                sys.stderr.write("Error: no direct location\n")
                sys.exit(1)
            

            if not location.startswith("http"):
                if not host:
                    sys.stderr.write("Redirect failed Host is empty\n")
                    sys.exit(1)
                location = f"http://{host}{location}"
            host, port, path = getInfo(location, current_host= host)
            socket.close()
            socket = sendMessage(host,port,path)
            response = receiveResponse(socket)
            header = response.partition("\r\n\r\n")[0]
            if "200 OK" in header:
                printBody(response, socket)
                break
            elif "301 Moved Permanently" in header or "302 Found" in header:
                continue
            else:
                sys.stderr.write("Error receive 200 OK code while redirecting")
                sys.exit(1)

        else:
         break
    
    if directNumber >= max:
            sys.stderr.write("Exceed the max direct limit")
            sys.exit(1)

        


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Invalid command line parameter\n")
        sys.exit(1)
    httpLink = sys.argv[1]
    host, port, path = getInfo(httpLink)
    clientSocket = sendMessage(host,port,path)
    response = receiveResponse(clientSocket)
    header = printBody(response,clientSocket)
    redirect(header, clientSocket,host)

    clientSocket.close()



if __name__ == "__main__":
    main()
