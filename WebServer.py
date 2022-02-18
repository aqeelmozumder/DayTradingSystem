import socket
import os
from _thread import *

def InitNewConnection(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    TransactionServerHost = "127.0.0.2"                           
    TransactionServerPort = 65433

    s.connect((TransactionServerHost, TransactionServerPort))                               
    while True:
        s.send(data)
        Response = s.recv(2048)
        s.close()
        break
  
    return Response                               

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
WebServerhost = '127.0.0.1'
WebServerPort = 65432
ThreadCount = 0
try:
    ServerSocket.bind((WebServerhost, WebServerPort))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)
print('listening on', (WebServerhost, WebServerPort))


def threaded_client(connection):
    connection.send(str.encode('Welcome to the Servern'))
    while True:
        data = connection.recv(2048)
        Price = InitNewConnection(data)
        reply = Price.decode('utf-8')
        
        if not data:
            print("No Data Received")
            break
        connection.sendall(str.encode(reply))
    
    connection.close()

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client(Client))
    # ThreadCount += 1
    # print('Thread Number: ' + str(ThreadCount))

ServerSocket.close()