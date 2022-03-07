import socket
from yahoo_fin import stock_info as si
import time
import config
import pickle
import uuid

QuoteServerHost = "127.0.0.1"  # Standard loopback interface address (localhost)
QuoteServerPort = 65438        # QuoteServerPort to listen on (non-privileged ports are > 1023)

def GetQuotePrice(data):
    receive_from_web = pickle.loads(data)
    
    if len(receive_from_web) > 1:
        stockSymbol = receive_from_web[2]
        quoteprice = round(si.get_live_price(stockSymbol), 2)
        username = receive_from_web[1]
        timestamp = time.time() * 1000
        cryptokey = str(uuid.uuid1())

        return [quoteprice, stockSymbol, username, timestamp, cryptokey]
    elif len(receive_from_web) == 1:
        return round(si.get_live_price(receive_from_web), 2)
    else:
        return "Missing parameters"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((config.QuoteServerHost, config.QuoteServerPort))
    s.listen()
    print('listening on', (config.QuoteServerHost, config.QuoteServerPort))
    
    while True:
        conn, addr = s.accept()
    
        print('Connected to: ' + addr[0] + ':' + str(addr[1]))
        data = conn.recv(2048)
        response = GetQuotePrice(data)
        if not data:
            print("No Data Received")
            break
        conn.sendall(pickle.dumps(response))
