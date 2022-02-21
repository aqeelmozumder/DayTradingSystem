import socket

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
WebServerHost = '127.0.0.1'
WebServerPort = 65432

print('Waiting for connection')
try:
    ClientSocket.connect((WebServerHost, WebServerPort))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(1024)
while True:
    Input = input('Please Type the Ticker: ')
    ClientSocket.send(str.encode(Input))
    Response = ClientSocket.recv(2048)
    print('Price is: ' + Response.decode('utf-8')  )

ClientSocket.close()