import socket
import pickle
from multiprocessing import Process
import config
import commands
import time


config.USER_COLLECTION.delete_many({})


def threaded_client(data):
    RequestData_from_Client = []
    Reply = "Received"

    # The Request from the client is Received here
    
    newdata = pickle.loads(data)
    RequestData_from_Client = newdata[0]
    transCount = newdata[1] 

    print(transCount)

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
        print("HELLO")
        if len(RequestData_from_Client) == 2:
            commands.Dumplog(RequestData_from_Client, transCount)      
                       
        else:
            commands.DumplogUser(RequestData_from_Client, transCount) 
                            
    elif command == 'DISPLAY_SUMMARY':
        commands.DisplaySummary(RequestData_from_Client, transCount)
        
    return Reply


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ServerSocket:
    try:
        ServerSocket.bind((config.WebServerHost, config.WebServerPort))
    except socket.error as e:
        print(str(e))
        
    print('Waitiing for a Connection..')
    ServerSocket.listen(5)
    print('listening on', (config.WebServerHost, config.WebServerPort))
    # transCount = 1
    while True:

        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        data = Client.recv(1024)
        Reply = threaded_client(data)
        # transCount +=1
        Client.sendall(str.encode(Reply))

