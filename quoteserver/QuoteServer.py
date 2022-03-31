import socket
import pickle
from _thread import *
from threading import *
import config



def main():
    # ThreadCount = 0
    #Init ClientSocket, WebServer host and port that the client will use to connect
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Bind the webserver
    BindWebServer(ServerSocket, config.QuoteServerHost, config.QuoteServerPort)

    ServerSocket.close()

#Bind and Start Listening
def BindWebServer(ServerSocket, QuoteServerHost, QuoteServerPort):
    
    try:
        ServerSocket.bind((QuoteServerHost, QuoteServerPort))
    except socket.error as e:
        print(str(e))
        
    print('Waitiing for a Connection..')
    ServerSocket.listen(5)
    print('listening on', (QuoteServerHost, QuoteServerPort))
    
    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        #Create a Thread for the Client/Connection
        start_new_thread(threaded_client, (Client, ))

def threaded_client(connection):
    WebSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    WebSocket.connect((config.WebContainerName, config.WebServerPort))
    # # print(len(stockSymbol))
    while True:
        data = connection.recv(1024)
        data = pickle.loads(data)
        newdata = pickle.dumps(data)
        WebSocket.send(newdata)
    #     Response = QuoteSocket.recv(2048)
    #     QuoteSocket.close()


main()