import socket

TransactionServerHost = "127.0.0.2"  # Standard loopback interface address (localhost)
TransactionServerPort = 65433        # QuoteServerPort to listen on (non-privileged ports are > 1023)

def InitNewConnection(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    QuoteServerHost = "127.0.0.6"                           
    QuoteServerPort = 65438

    s.connect((QuoteServerHost, QuoteServerPort))                               
    while True:
        s.send(data)
        Response = s.recv(2048)
        quotedata = Response
        s.close()
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

        quotedata = InitNewConnection(data)
        if not data:
            print("No Data Received")
            break
        conn.sendall(quotedata)
        


