import socket
import pickle
from _thread import *
from threading import *
import config
import commands
import time

lock = Lock()
config.USER_COLLECTION.delete_many({})


def main():
    # ThreadCount = 0
    #Init ClientSocket, WebServer host and port that the client will use to connect
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Bind the webserver
    BindWebServer(ServerSocket, config.WebServerHost, config.WebServerPort)

    ServerSocket.close()

#Bind and Start Listening
def BindWebServer(ServerSocket, WebServerHost, WebServerPort):
    
    try:
        ServerSocket.bind((WebServerHost, WebServerPort))
    except socket.error as e:
        print(str(e))
        
    print('Waitiing for a Connection..')
    ServerSocket.listen(5)
    print('listening on', (WebServerHost, WebServerPort))
    
    while True:
        connection, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        #Create a Thread for the Client/Connection
        # start_new_thread(threaded_client, (Client, ))

        RequestData_from_Client = []
        connection.send(str.encode('Connection Threaded'))
        transCount = 1
    # while True:
        data = connection.recv(1024)
        Reply = "Received"
        # The Request from the client is Received here
        try:
            RequestData_from_Client = pickle.loads(data)
            # print(RequestData_from_Client)
            command = RequestData_from_Client[0]
            if command == 'ADD':
                Reply = commands.Add(RequestData_from_Client, transCount)
            elif command == 'QUOTE':
                Reply = commands.Quote(RequestData_from_Client, transCount)
            elif command == 'BUY':
                Reply = commands.Buy(RequestData_from_Client, transCount)
            elif command == 'COMMIT_BUY':
                Reply = commands.CommitBuy(RequestData_from_Client, transCount)
            elif command == 'CANCEL_BUY':
                Reply = commands.CancelBuy(RequestData_from_Client, transCount)
            elif command == 'SELL':
                Reply = commands.Sell(RequestData_from_Client, transCount)               
            elif command == 'COMMIT_SELL':
                Reply = commands.CommitSell(RequestData_from_Client, transCount)            
            elif command == 'CANCEL_SELL':
                Reply = commands.CancelSell(RequestData_from_Client, transCount)                
            elif command == 'SET_BUY_AMOUNT':
                Reply = commands.SetBuyAmount(RequestData_from_Client, transCount)                
            elif command == 'CANCEL_SET_BUY':
                Reply = commands.CancelSetBuy(RequestData_from_Client, transCount)                
            elif command == 'SET_BUY_TRIGGER':
                Reply = commands.SetBuyTrigger(RequestData_from_Client, transCount)                
            elif command == 'SET_SELL_AMOUNT':
                Reply = commands.SetSellAmount(RequestData_from_Client, transCount)                
            elif command == 'SET_SELL_TRIGGER':
                Reply = commands.SetSellTrigger(RequestData_from_Client, transCount)                
            elif command == 'CANCEL_SET_SELL':
                Reply = commands.CancelSetSell(RequestData_from_Client, transCount)                
            elif command == 'DUMPLOG':
                if len(RequestData_from_Client) == 2:
                    commands.Dumplog(RequestData_from_Client, transCount)                    
                else:
                    commands.DumplogUser(RequestData_from_Client, transCount)                    
            elif command == 'DISPLAY_SUMMARY':
                commands.DisplaySummary(RequestData_from_Client, transCount)
        except EOFError:
            # print("err", data)
            break
        transCount += 1
        
        connection.sendall(str.encode(Reply))
    connection.close()

                          

# def threaded_client(connection):
    # RequestData_from_Client = []
    # connection.send(str.encode('Connection Threaded'))
    # transCount = 1
    # while True:
    #     data = connection.recv(1024)
    #     Reply = "Received"
    #     # The Request from the client is Received here
    #     try:
    #         RequestData_from_Client = pickle.loads(data)
    #         # print(RequestData_from_Client)
    #         command = RequestData_from_Client[0]
    #         if command == 'ADD':
    #             Reply = commands.Add(RequestData_from_Client, transCount)
    #         elif command == 'QUOTE':
    #             Reply = commands.Quote(RequestData_from_Client, transCount)
    #         elif command == 'BUY':
    #             Reply = commands.Buy(RequestData_from_Client, transCount)
    #         elif command == 'COMMIT_BUY':
    #             Reply = commands.CommitBuy(RequestData_from_Client, transCount)
    #         elif command == 'CANCEL_BUY':
    #             Reply = commands.CancelBuy(RequestData_from_Client, transCount)
    #         elif command == 'SELL':
    #             Reply = commands.Sell(RequestData_from_Client, transCount)               
    #         elif command == 'COMMIT_SELL':
    #             Reply = commands.CommitSell(RequestData_from_Client, transCount)            
    #         elif command == 'CANCEL_SELL':
    #             Reply = commands.CancelSell(RequestData_from_Client, transCount)                
    #         elif command == 'SET_BUY_AMOUNT':
    #             Reply = commands.SetBuyAmount(RequestData_from_Client, transCount)                
    #         elif command == 'CANCEL_SET_BUY':
    #             Reply = commands.CancelSetBuy(RequestData_from_Client, transCount)                
    #         elif command == 'SET_BUY_TRIGGER':
    #             Reply = commands.SetBuyTrigger(RequestData_from_Client, transCount)                
    #         elif command == 'SET_SELL_AMOUNT':
    #             Reply = commands.SetSellAmount(RequestData_from_Client, transCount)                
    #         elif command == 'SET_SELL_TRIGGER':
    #             Reply = commands.SetSellTrigger(RequestData_from_Client, transCount)                
    #         elif command == 'CANCEL_SET_SELL':
    #             Reply = commands.CancelSetSell(RequestData_from_Client, transCount)                
    #         elif command == 'DUMPLOG':
    #             if len(RequestData_from_Client) == 2:
    #                 commands.Dumplog(RequestData_from_Client, transCount)                    
    #             else:
    #                 commands.DumplogUser(RequestData_from_Client, transCount)                    
    #         elif command == 'DISPLAY_SUMMARY':
    #             commands.DisplaySummary(RequestData_from_Client, transCount)
    #     except EOFError:
    #         # print("err", data)
    #         break
    #     transCount += 1
        
    #     connection.sendall(str.encode(Reply))
    # connection.close()


main()
