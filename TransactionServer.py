import socket
import pymongo
import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
logDB = myclient["seng468"]
logFileCollection = logDB["logfile"]

TransactionServerHost = "127.0.0.1"  # Standard loopback interface address (localhost)
TransactionServerPort = 65433        # QuoteServerPort to listen on (non-privileged ports are > 1023)

def InitNewConnection(data):
    QuoteSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    QuoteServerHost = "127.0.0.1"                           
    QuoteServerPort = 65438

    QuoteSocket.connect((QuoteServerHost, QuoteServerPort))                               
    while True:
        QuoteSocket.send(data)
        Response = s.recv(2048)
        quotedata = Response
        QuoteSocket.close()
        break
                                  
    return quotedata



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((TransactionServerHost, TransactionServerPort))
    s.listen()
    print('listening on', (TransactionServerHost, TransactionServerPort))
    
    while True:
        conn, addr = s.accept()
    
        print('Connected to: ' + addr[0] + ':' + str(addr[1]))
        data = conn.recv(2048)
        print("HERE WE ARE IN THE TRANSACTion server 1")
        print(data)
        #Bunch of Cases

        quoteData = InitNewConnection(data)
        print("here in trans 2")
        print(quoteData)
        if not data:
            print("No Data Received")
            break
        conn.sendall(quoteData)
        


