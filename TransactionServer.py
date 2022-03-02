import socket
import time
import config

def InitNewConnection(data):
    QuoteSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    QuoteSocket.connect((config.QuoteServerHost, config.QuoteServerPort))
                            
    while True:
        QuoteSocket.send(data)
        Response = s.recv(2048)
        quotedata = Response
        QuoteSocket.close()
        break

    return quotedata

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((config.TransactionServerHost, config.TransactionServerPort))
    s.listen()
    print('listening on', (config.TransactionServerHost, config.TransactionServerPort))
    
    while True:
        conn, addr = s.accept()
        print('Connected to: ' + addr[0] + ':' + str(addr[1]))

        data = conn.recv(2048)
        quoteData = InitNewConnection(data)

        if not data:
            print("No Data Received")
            break

        conn.sendall(quoteData)
