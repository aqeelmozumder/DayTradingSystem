import socket
import pickle
import config
import commands
import ssl
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


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
        if len(RequestData_from_Client) == 2:
            commands.Dumplog(RequestData_from_Client, transCount)      
            print("Testlog Should be Generated in this Server")        
        else:
            commands.DumplogUser(RequestData_from_Client, transCount) 
            print("Testlog Should be Generated in this Server") 
                            
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

    while True:

        Client, address = ServerSocket.accept()
        secureClientSocket = ssl.wrap_socket(Client,server_side=True, certfile="./server/host.cert", keyfile="./server/host.key",ssl_version=ssl.PROTOCOL_TLS_SERVER);

        print('Connected to: ' + address[0] + ':' + str(address[1]))

        data = secureClientSocket.recv(1024)
        Reply = threaded_client(data)
        
        secureClientSocket.sendall(str.encode(Reply))