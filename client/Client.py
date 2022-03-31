import socket
import sys
import json
import pickle
import config
import time

#Try Connecting to the WebServer and if successful return True

def ConnectToWebServer(ClientSocket, WebContainerName, WebServerPort):

    print('Waiting for connection')
    try:
        ClientSocket.connect(('seng468_webserver_1', 65432))
        #To Run Local:
        # ClientSocket.connect((WebContainerName, WebServerPort))
        return True
    except socket.error as e:
        print(str(e))
        return False


#Parse the file and send each line of data as a request to the Webserver
def ParseAndSend():
    
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
            Data = pickle.dumps([Input, count])
            
            ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            ClientSocket.connect((config.WebContainerName, config.WebServerPort))
            ClientSocket.send(Data)
            # time.sleep(0.1)
            Response = ClientSocket.recv(4096)
            # print(count)
            count = count +1
            ClientSocket.close()
    
    return 

def main():

    ParseAndSend()

main()