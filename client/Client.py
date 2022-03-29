from concurrent.futures import thread
import socket
import pickle
import config
import time
from _thread import *
from threading import *
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from FileParser import Parser, log



def OpenNewandSendLogCommand(Logfile):
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                
    
    # #Check ConnectToWebServer
    Connection = ConnectToWebServer("NoThread",ClientSocket, config.WebContainerName, config.WebServerPort)

    # #If the the connection is succesful then we will parse the file and send the data to the WebServer
    if(Connection):
        print(Logfile[0])
        Data = pickle.dumps(Logfile[0])
        ClientSocket.send(Data)
        # time.sleep(0.2)

    ClientSocket.close()

def Connect(Threadname, AllUsersData):
    #Init ClientSocket, WebServer host and port that the client will use to connect
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                
    
    # #Check ConnectToWebServer
    Connection = ConnectToWebServer(Threadname, ClientSocket, config.WebContainerName, config.WebServerPort)

    # #If the the connection is succesful then we will parse the file and send the data to the WebServer
    if(Connection):
            ParseAndSend(Threadname, ClientSocket, AllUsersData)
    
    print("Closing Connection")
    ClientSocket.close()



#Try Connecting to the WebServer and if successful return True
def ConnectToWebServer(Threadname, ClientSocket, WebContainerName, WebServerPort):

    # print('Waiting for connection: ', Threadname)
    try:
        # ClientSocket.connect((WebContainerName, WebServerPort))
        ClientSocket.connect(("nginx", 5100))
        return True
    except socket.error as e:
        print(str(e))
        return False

#Parse the file and send each line of data as a request to the Webserver
def ParseAndSend(Name, ClientSocket, Userdata):
    
    for x in range(len(Userdata)):
    #Send the list of data using Pickle Dumps
        print(x)
        Data = pickle.dumps(Userdata[x])
        ClientSocket.send(Data)
        # time.sleep(0.1)
        Response = ClientSocket.recv(4096)

    
    #Response = ClientSocket.recv(2048)
    return Response.decode('utf-8')

def main():
    AllUsersData = Parser()
    Logfile = log()

    with ThreadPoolExecutor(max_workers=5) as executor:
        for x in range(len(AllUsersData)):
            executor.submit(Connect, "Client"+str(x), AllUsersData[x])
        
    print('All Clients have completed their Requests')
    OpenNewandSendLogCommand(Logfile)

    



main()
