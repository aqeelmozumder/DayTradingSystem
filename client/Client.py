import socket
import pickle
import config
import time

#Try Connecting to the WebServer and if successful return True
def ConnectToWebServer(ClientSocket, WebContainerName, WebServerPort):

    print('Waiting for connection')
    try:
        ClientSocket.connect((WebContainerName, WebServerPort))
        return True
    except socket.error as e:
        print(str(e))
        return False

#Parse the file and send each line of data as a request to the Webserver
def ParseAndSend(ClientSocket):
    with open("./client/Commands.txt", "r") as file:
        count = 1
        Input : list
        for lines in file:
            Input = []
            #This is to remove the enumeration in the file which is included with the Squrare brackets, like remove [1],[2] and so on
            RemoveCharacters = "[" + str(count) + "]"

            #Will strip [1],[2] etc. will also remove whitespaces and trailing new lines. Then split them between the commas
            Input = lines.strip(RemoveCharacters).strip(" ").rstrip("\n").rstrip(" ").split(",")

            #Send the list of data using Pickle Dumps
            Data = pickle.dumps(Input)

            ClientSocket.send(Data)
            time.sleep(0.1)
            Response = ClientSocket.recv(4096)
            print(Response.decode('utf-8'))
            count = count +1
    #file.close()
    #Response = ClientSocket.recv(2048)
    return Response.decode('utf-8')

def main():
    #Init ClientSocket, WebServer host and port that the client will use to connect
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                

    #Check ConnectToWebServer
    Connection = ConnectToWebServer(ClientSocket, config.WebContainerName, config.WebServerPort)

    #If the the connection is succesful then we will parse the file and send the data to the WebServer
    if(Connection):
        ParseAndSend(ClientSocket)
        #print(Response)

    ClientSocket.close()

main()