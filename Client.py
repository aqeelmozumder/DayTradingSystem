import socket
import sys
import json
import pickle
import config

#Try Connecting to the WebServer and if successful return True
def ConnectToWebServer(ClientSocket, WebServerHost, WebServerPort):

    print('Waiting for connection')
    try:
        ClientSocket.connect((WebServerHost, WebServerPort))
        return True
    except socket.error as e:
        print(str(e))
        return False

#Parse the file and send each line of data as a request to the Webserver
def ParseAndSend(ClientSocket):
    with open("Commands.txt", "r") as file:
        count = 1
        Input : list
        for lines in file:
            Input = []
            #This is to remove the enumeration in the file which is included with the Squrare brackets, like remove [1],[2] and so on
            RemoveCharacters = "[" + str(count) + "]"

            #Will strip [1],[2] etc. will also remove whitespaces and trailing new lines. Then split them between the commas
            Input = lines.strip(RemoveCharacters).strip(" ").rstrip("\n").rstrip(" ").split(",")
            print("here we are in the client 1")
            print(type(Input))
            print(Input)
            #Send the list of data using Pickle Dumps
            Data = pickle.dumps(Input)

            ClientSocket.send(Data)
            Response = ClientSocket.recv(4096)
            print(Response.decode('utf-8'))
            count = count +1
    file.close()
    Response = ClientSocket.recv(2048)
    return Response.decode('utf-8')

def main():
    #Init ClientSocket, WebServer host and port that the client will use to connect
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                

    #Check ConnectToWebServer
    Connection = ConnectToWebServer(ClientSocket, config.WebServerHost, config.WebServerPort)

    #If the the connection is succesful then we will parse the file and send the data to the WebServer
    if(Connection):
        Response = ParseAndSend(ClientSocket)
        print(Response)

    ClientSocket.close()

main()
