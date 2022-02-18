import socket
from yahoo_fin import stock_info as si

QuoteServerHost = "127.0.0.6"  # Standard loopback interface address (localhost)
QuoteServerPort = 65438        # QuoteServerPort to listen on (non-privileged ports are > 1023)

def GetQuotePrice(data):

    ticker = data.decode('utf-8')

    # print("the ticker is: " + ticker)
    quoteprice = si.get_live_price(ticker)

    return str(quoteprice)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((QuoteServerHost, QuoteServerPort))
    s.listen()
    print('listening on', (QuoteServerHost, QuoteServerPort))
    
    while True:
        conn, addr = s.accept()
    
        print('Connected to: ' + addr[0] + ':' + str(addr[1]))
        data = conn.recv(2048)
        Price = GetQuotePrice(data)
        if not data:
            print("No Data Received")
            break
        conn.sendall(str.encode(Price))