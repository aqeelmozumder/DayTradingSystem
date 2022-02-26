import socket
import os
import json
import pickle
from _thread import *
import pymongo
import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
logDB = myclient["seng468"]
logFileCollection = logDB["logfile"]
userCollection = logDB["userCollection"]
userCollection.delete_many({})

def getStockPrice(stockSymbol):
    #this needs to get stock price from quote server
    #will just return dollar value of stock
    return 5.00

def insertBuyOrder(data):
    username = data[1]
    amount = data[3]
    newOrder = {
        "buyAmount": round(float(amount), 2),
        "stockSymbol": data[2],
        "orderTime": time.time()
    }
    newOrderItem = {
        "$push":
            { "buyOrders": newOrder} 
    }
    userCollection.update_one({ "username": username }, newOrderItem)
    return

def buyStock(buyOrder, username):
    #this is not really what we want to do here
    #need to send to transaction server
    #get quote from quote server
    #update user's "stocks" and balance from transaction server
    
    stockSymbol = buyOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numStockBuy = int(buyOrder["buyAmount"] / stockPrice)
    #ensure stock exists in users stocks
    if userCollection.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0:
        #user has previously had that stock, increment that stock's numberOfStock
        userCollection.update_one(
            { "username": username, "stocks.stockSymbol": stockSymbol },
            { "$inc": { "stocks.$.numberOfStock": numStockBuy } },
            upsert=True
        )
    else:
        #user has not previously had that stock, add to stocks array
        userCollection.update_one(
            { "username": username },
            { "$addToSet": { "stocks": { "stockSymbol": stockSymbol, "numberOfStock": numStockBuy } } },
        )
    
    costToUser = round(float(numStockBuy * stockPrice), 2)
    userCollection.update_one(
        { "username": username },
        { "$inc": { "balance": -costToUser } }
    )
    return

def getLastBuyOrder(username):
    user = userCollection.find_one({ "username": username })
    if len(user["buyOrders"]) > 0:
        return user["buyOrders"][-1]
    else:
        return False

def removeLastBuyOrder(username):
    #remove buy order from array of buy orders
    userCollection.update_one({ "username": username }, { "$pop": { "buyOrders": 1 } })
    return

def insertSellOrder(data):
    username = data[1]
    amount = data[3]
    newOrder = {
        "sellAmount": round(float(amount), 2),
        "stockSymbol": data[2],
        "orderTime": time.time()
    }
    newOrderItem = {
        "$push":
            { "sellOrders": newOrder} 
    }
    userCollection.update_one({ "username": username }, newOrderItem)
    return

def sellStock(sellOrder, username):
    #this is not at all what we want to do here
    #need to send to transaction server
    #get quote from quote server
    #update user's "stocks" and balance

    stockSymbol = sellOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numStockSell = int(sellOrder["sellAmount"] / stockPrice)
    #ensure stock exists in user's stocks
    if userCollection.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0:
        userCollection.update_one(
            { "username": username, "stocks.stockSymbol": stockSymbol },
            { "$inc": { "stocks.$.numberOfStock": -numStockSell } },
            upsert=True
        )
    else:
        #error about not having the stock
        return
    depositToUser = round(float(numStockSell * stockPrice), 2)
    userCollection.update_one(
        { "username": username },
        { "$inc": { "balance": depositToUser } }
    )
    return

def getLastSellOrder(username):
    user = userCollection.find_one({ "username": username })
    if len(user["sellOrders"]) > 0:
        return user["sellOrders"][-1]
    else:
        return False

def removeLastSellOrder(username):
    #remove sell order from array of sell orders
    userCollection.update_one({ "username": username }, { "$pop": { "sellOrders": 1 } })
    return

def userBalance(username):
    user = userCollection.find_one({ "username": username })
    return user["balance"]

def addFunds(data):
    username = data[1]
    amount = data[2]
    userCollection.update_one(
        { "username": username },
        { "$inc": { "balance": round(float(amount), 2) } }
    )
    return

def doesUserExist(username):
    return userCollection.count_documents({ "username": username }) > 0

def insertNewUserTransaction(username, newTransaction):
    newUser = {
        "username": username,
        "transactions": [
            newTransaction
        ],
        "balance": 0.00,
        "holdBalance": 0.00,
        "stocks": [],
        "buyOrders": [],
        "sellOrders": [],
        "setBuys": [],
        "buyTriggers": [],
        "setSells": [],
        "sellTriggers": [],
        "stocksHoldAccount": []
    }
    userCollection.insert_one(newUser)
    return

def insertExistingUserTransaction(username, newTransaction):
    newValues = {
        "$push":
            { "transactions": newTransaction } 
    }
    
    userCollection.update_one({ "username": username }, newValues)
    return

def insertNewTransaction(username, newTransaction):
    if not doesUserExist(username):
        insertNewUserTransaction(username, newTransaction)
    else:
        insertExistingUserTransaction(username, newTransaction)
    return

def insertUserAndAmountTransaction(data, transCount):
    command = data[0]
    username = data[1]
    amount = data[2]
    newTransaction = {
        "type": "UserCommand",
        "timeStamp": time.time(),
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username,
        "funds": round(float(amount), 2)
    }
    insertNewTransaction(username, newTransaction)
    return

def insertUserAndStockSymbolTransaction(data, transCount):
    command = data[0]
    username = data[1]
    stockSymbol = data[2]
    newTransaction = {
        "type": "UserCommand",
        "timeStamp": time.time(),
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username,
        "stockSymbol": stockSymbol
    }
    insertNewTransaction(username, newTransaction)
    return

def insertUserStockSymbolAndAmountTransaction(data, transCount):
    command = data[0]
    username = data[1]
    stockSymbol = data[2]
    amount = data[3]
    newTransaction = {
        "type": "UserCommand",
        "timeStamp": time.time(),
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username,
        "stockSymbol": stockSymbol,
        "funds": round(float(amount), 2)
    }
    insertNewTransaction(username, newTransaction)
    return

def insertUserTransaction(data, transCount):
    command = data[0]
    username = data[1]
    newTransaction = {
        "type": "UserCommand",
        "timeStamp": time.time(),
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username
    }
    insertNewTransaction(username, newTransaction)
    return

def insertUserAndFilenameTransaction(data, transCount):
    command = data[0]
    username = data[1]
    filename = data[2]
    newTransaction = {
        "type": "UserCommand",
        "timeStamp": time.time(),
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username,
        "filename": filename
    }
    insertNewTransaction(username, newTransaction)
    return

def insertFilenameTransaction(data, transCount):
    command = data[0]
    filename = data[1]
    newTransaction = {
        "type": "UserCommand",
        "timeStamp": time.time(),
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "filename": filename
    }
    insertNewTransaction('ADMIN', newTransaction)
    return

def Add(data, transCount):
    #user, amount
    #add given amout to users account
    insertUserAndAmountTransaction(data, transCount)
    addFunds(data)
    return
    
def Quote(data, transCount):
    #user,StockSymbol
    #get current quote for the stock for specified user
    insertUserAndStockSymbolTransaction(data, transCount)
    #need more here on interaction with quote server
    return
    
def Buy(data, transCount):
    #user,StockSymbol,amount
    #buy dollar amount of the stock for user at current price
    #users account must be greater or equal to amnt of purchase
    #user asked to confirm or cancel
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    if userBalance(data[1]) >= round(float(data[3]), 2):
        insertBuyOrder(data)
        return
    else:
        #need not enough funds error
        return
    return
    
def CommitBuy(data, transCount):
    #user
    #commits the most recently executed BUY command
    #user must have executed Buy within previous 60 secs
    #users cash account decrease by amount purchased
    #users account for given stock increased by purchase amount
    username = data[1]
    insertUserTransaction(data, transCount)
    buyOrder = getLastBuyOrder(username)
    if buyOrder:
        if (buyOrder["orderTime"] >= time.time() - 60):
            if userBalance(username) >= buyOrder["buyAmount"]:
                buyStock(buyOrder, username)
            else:
                #error for not enough balance
                return
        else:
            #error for 60 seconds having passed
            return
    return
    
def CancelBuy(data, transCount):
    #user
    #cancels most recently executed BUY command
    #user must have executed Buy within previous 60 secs
    #last Buy command cancelled and any allocated system resourses reset and released
    username = data[1]
    insertUserTransaction(data, transCount)
    buyOrder = getLastBuyOrder(username)
    if buyOrder:
        if buyOrder["orderTime"] >= time.time() - 60:
            removeLastBuyOrder(username)
        else:
            #error for 60 seconds having passed
            return
    return
    
def Sell(data, transCount):
    #user, StockSymbol,amount
    #sell specified dollar amnt of the stock currently held by specified user
    #users acnt for stock must be greater or equal to amnt being sold
    #user asked to confirm or cancel
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    if userBalance(data[1]) >= round(float(data[3]), 2):
        insertSellOrder(data)
        return
    else:
        #need not enough funds error
        return
    return
    return
    
def CommitSell(data, transCount):
    #user
    #cancels most recently executed SELL
    #user must have executed Sell within previous 60 secs
    #users account for given stock decremented by the sale amnt
    #the users cash acnt increased by sell amnt
    username = data[1]
    insertUserTransaction(data, transCount)
    sellOrder = getLastSellOrder(username)
    if sellOrder:
        if (sellOrder["orderTime"] >= time.time() - 60):
            if userBalance(username) >= sellOrder["sellAmount"]:
                sellStock(sellOrder, username)
            else:
                #error for not enough balance
                return
        else:
            #error for 60 seconds having passed
            return
    return
    
def CancelSell(data, transCount):
    #user
    #cancels most recently executed SELL
    #user must have executed Sell within previous 60 secs
    #last SELL command cancelled and any allocated system resourses reset and released
    username = data[1]
    insertUserTransaction(data, transCount)
    sellOrder = getLastSellOrder(username)
    if sellOrder:
        if sellOrder["orderTime"] >= time.time() - 60:
            removeLastSellOrder(username)
        else:
            #error for 60 seconds having passed
            return
    return

def SetBuyAmount(data, transCount):
    #user,StockSymbol,amount
    #sets defined amount of given stock to buy when the current stock price less or equal to BUY_TRIGGER
    #users cash acnt must be >= buy amnt at time transaction occurs
    #hold accnt created for the buy transaction to hold the specified amnt in reserve for when transaction triggered
    #users cash acnt decremented by specified amount
    #when trigger point reached the users stock account updated to reflect the BUY transaction
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    if userBalance(username) >= amount:
        if userCollection.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0:
            #user has previous setBuy, set that setBuy amount to new value
            userCollection.update_one(
                { "username": username, "setBuy.stockSymbol": stockSymbol },
                { "$set": { "setBuy.$.amount": amount } },
                upsert=True
            )
        else:
            #user does not have a setBuy for that stock
            userCollection.update_one(
                { "username": username },
                { "$addToSet": { "setBuy": { "stockSymbol": stockSymbol, "amount": amount } } },
            )
        userCollection.update_one(
            { "username": username },
            { "$inc": { "balance": -amount } }
        )
        userCollection.update_one(
            { "username": username },
            { "$inc": { "holdBalance": amount } }
        )
    else:
        #error for not enough funds
        return
    return

def CancelSetBuy(data, transCount):
    #user,StockSymbol
    #cancels a SET_BUY command for given stock
    #must have been a SET_BUY command issued for given stock by user
    #all accounts are reset to values they would have had had the SET_BUY not been triggered
    #the BUY_TRIGGER for the given user and stock also cancelled
    username = data[1]
    stockSymbol = data[2]
    insertUserAndStockSymbolTransaction(data, transCount)
    if userCollection.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0:
        userCollection.update_one(
            { "username": username },
            { "$pull": { "setBuy": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
        )
    if userCollection.count_documents({ "username": username, "buyTriggers.stockSymbol": stockSymbol }) > 0:
        userCollection.update_one(
            { "username": username },
            { "$pull": { "buyTriggers": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
        )
    return
    
def SetBuyTrigger(data, transCount):
    #NOT IN FIRST LOG FILE
    #user,StockSymbol,amount
    #Sets the trigger point base on the current stock price when any SET_BUY will execute
    #user must have specified a SET_BUY_AMOUNT prior to setting TRIGGER
    #set of the users buy triggers is updated to include the specified trigger
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = data[3]
    
    if userCollection.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0:
        if userCollection.count_documents({ "username": username, "buyTriggers.stockSymbol": stockSymbol }) > 0:
            #user has previous buy trigger for that stock, set that buy trigger amount to new value
            userCollection.update_one(
                { "username": username, "buyTriggers.stockSymbol": stockSymbol },
                { "$set": { "buyTriggers.$.amount": amount } },
                upsert=True
            )
        else:
            #user does not have a buy trigger for that stock
            userCollection.update_one(
                { "username": username },
                { "$addToSet": { "buyTrigger": { "stockSymbol": stockSymbol, "amount": amount } } },
            )
    else:
        #user does not have a setBuy for that stock
        #return error that they can't set buy trigger until have a set buy
        return
    return
    
def SetSellAmount(data, transCount):
    #user,StockSymbol,amount
    #sets defined amnt of stock to sell when current stock price equal or greater than sell trigger point
    #user must have the specified amnt of stock in their acnt for that stock
    #trigger init'd for user/stock combo, but not complete until SET_SELL_TRIGGER executed
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    stockPrice = getStockPrice(stockSymbol)
    amount = round(float(data[3]), 2)
    numStocksSellAmount = int(amount/stockPrice)
    #ensure user has stock
    if userCollection.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0:
        userStockInfo = userCollection.find_one({ "username": username, "stocks.stockSymbol": stockSymbol })["stocks"]
        stockInfo = next((x for x in userStockInfo if x["stockSymbol"] == stockSymbol), None)
        if stockInfo["numberOfStock"] >= numStocksSellAmount:
            if userCollection.count_documents({ "username": username, "setSell.stockSymbol": stockSymbol }) > 0:
                #user has previous setSell, set that setSell amount to new value
                userCollection.update_one(
                    { "username": username, "setSell.stockSymbol": stockSymbol },
                    { "$set": { "setSell.$.amount": amount } },
                    upsert=True
                )
            else:
                #user does not have a setSell for that stock
                userCollection.update_one(
                    { "username": username },
                    { "$addToSet": { "setSell": { "stockSymbol": stockSymbol, "amount": amount } } },
                )
        else:
            #error for not enough stocks for current value
            return
    else:
        #error for user not having that stock
        return
    return
    
def SetSellTrigger(data, transCount):
    #user,StockSymbol,amount
    #sets stock price triffer point for executing any SET_SELL triggers associated with the given stock and user
    #user must have spec'd a SET_SELL_AMOUNT prior to SET_SELL_TRIGGER
    #reserve acnt created for spec'd amnt of stock
    #user acnt for stock reduced by max number of stocks that could be purchased
    #set of the users sell triggers is updated to include the specified trigger
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    #ensure user has stock
    if userCollection.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0:
        #ensure user has set sell for that stock
        if userCollection.count_documents({ "username": username, "setSell.stockSymbol": stockSymbol }) > 0:
            if userCollection.count_documents({ "username": username, "sellTriggers.stockSymbol": stockSymbol }) > 0:
                #user has previous sell trigger for that stock, set that sell trigger amount to new value
                userCollection.update_one(
                    { "username": username, "sellTriggers.stockSymbol": stockSymbol },
                    { "$set": { "sellTriggers.$.amount": amount } },
                    upsert=True
                )
            else:
                #user does not have a buy trigger for that stock
                userCollection.update_one(
                    { "username": username },
                    { "$addToSet": { "sellTrigger": { "stockSymbol": stockSymbol, "amount": amount } } },
                )
            numberOfStocks = int(getStockPrice(stockSymbol) * amount)
            #remove stocks from user stocks
            userCollection.update_one(
                { "username": username, "stocks.stockSymbol": stockSymbol },
                { "$inc": { "stocks.$.numberOfStock": -numberOfStocks } }
            )
            #add stocks to user stocksHoldAccount
            if userCollection.count_documents({ "username": username, "stocksHoldAccount.stockSymbol": stockSymbol }) > 0:
                #user has previously had that stock, increment that stock's numberOfStock
                userCollection.update_one(
                    { "username": username, "stocksHoldAccount.stockSymbol": stockSymbol },
                    { "$inc": { "stocksHoldAccount.$.numberOfStock": numberofStocks } },
                    upsert=True
                )
            else:
                #user has not previously had that stock, add to stocks array
                userCollection.update_one(
                    { "username": username },
                    { "$addToSet": { "stocksHoldAccount": { "stockSymbol": stockSymbol, "numberOfStock": numberOfStocks } } },
                )
        else:
            #user does not have a setBell for that stock
            #return error that they can't set sell trigger until have a set buy
            return
    else:
        #error that user doens't have any of those stocks
        return
    return
    
def CancelSetSell(data, transCount):
    #user,StockSymbol
    #cancels the SET_SELL associated with the stock and user
    #use must have had a previously set SET_SELL for stock
    #set of the users sell triggers is updated to remove the sell triffer associated with stock
    #all user acnt info reset to values would have been if SET_SELL had not been issued
    insertUserAndStockSymbolTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    if userCollection.count_documents({ "username": username, "setSell.stockSymbol": stockSymbol }) > 0:
        userCollection.update_one(
            { "username": username },
            { "$pull": { "setSell": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
        )
    if userCollection.count_documents({ "username": username, "sellTriggers.stockSymbol": stockSymbol }) > 0:
        userCollection.update_one(
            { "username": username },
            { "$pull": { "sellTriggers": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
        )
    return
    
def DumplogUser(data, transCount):
    #NOT IN FIRST LOG FILE
    #user,filename
    #print history of users transactions to the spec'd file
    insertUserAndFilenameTransaction(data, transCount)
    return
    
def Dumplog(data, transCount):
    #filename
    #print to the spec'd file the complete set of transactions that have occured in system
    #can only be executed from the supervisor/root/admin account
    insertFilenameTransaction(data, transCount)
    return
    
def DisplaySummary(data, transCount):
    #user
    #provides summary to client of the users transaction history and the current status of their accounts
    #as well as any set buy or sell triggers and their parameters
    insertUserTransaction(data, transCount)
    return

def main():
    
    #Init ClientSocket, WebServer host and port that the client will use to connect
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    WebServerhost = '127.0.0.1'
    WebServerPort = 65432

    #Bind the webserver
    BindWebServer(ServerSocket, WebServerhost, WebServerPort)

    ServerSocket.close()

#Bind and Start Listening
def BindWebServer(ServerSocket, WebServerhost, WebServerPort):
    
    try:
        ServerSocket.bind((WebServerhost, WebServerPort))
    except socket.error as e:
        print(str(e))
        
    print('Waitiing for a Connection..')
    ServerSocket.listen(5)
    print('listening on', (WebServerhost, WebServerPort))
    
    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
#Create a Thread for the Client/Connection
        start_new_thread(threaded_client, (Client, ))



# Connect To Transaction Servr
def ConnectToTransactionServer(data):
    TransactionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    TransactionServerHost = "0.0.0.0"                           
    TransactionServerPort = 9998

    TransactionSocket.connect((TransactionServerHost, TransactionServerPort))

    while True:
        TransactionSocket.send(data)
        Response = TransactionSocket.recv(2048)
        TransactionSocket.close()
        break
  
    return Response.decode('utf-8')                            


def threaded_client(connection):
    RequestData_from_Client = []
    connection.send(str.encode('Connection Threaded'))
    transCount = 0
    while True:
        data = connection.recv(4096)

        # The Request from the client is Received here
        try:
            RequestData_from_Client = pickle.loads(data)
        except EOFError:
            print("error", data)

        #********** //:TODO  ***********
        # Try Printing these to understand: RequestData_from_Client[0], Print RequestData_from_Client[1] and so on but needs a limit

        command = RequestData_from_Client[0]

        if command == 'ADD':
            #ADD,username,amount
            Add(RequestData_from_Client, transCount)
        elif command == 'QUOTE':
            #QUOTE,username,stockSymbol
            Quote(RequestData_from_Client, transCount)
        elif command == 'BUY':
            #BUY,username,stockSymbol,amount
            Buy(RequestData_from_Client, transCount)
        elif command == 'COMMIT_BUY':
            #COMMIT_BUY,username
            CommitBuy(RequestData_from_Client, transCount)
        elif command == 'CANCEL_BUY':
            #CANCEL_BUY,username
            CancelBuy(RequestData_from_Client, transCount)

        elif command == 'SELL':
            #SELL,username,stockSymbol,amount
            Sell(RequestData_from_Client, transCount)

        elif command == 'COMMIT_SELL':
            #COMMIT_SELL,username
            CommitSell(RequestData_from_Client, transCount)

        elif command == 'CANCEL_SELL':
            #CANCEL_SELL,username
            CancelSell(RequestData_from_Client, transCount)

        elif command == 'SET_BUY_AMOUNT':
            #SET_BUY_AMOUNT,username,StockSymbol,amount
            SetBuyAmount(RequestData_from_Client, transCount)

        elif command == 'CANCEL_SET_BUY':
            #CANCEL_SET_BUY,username,StockSymbol
            CancelSetBuy(RequestData_from_Client, transCount)

        elif command == 'SET_BUY_TRIGGER':
            #SET_BUY_TRIGGER,username,StockSymbol,amount
            SetBuyTrigger(RequestData_from_Client, transCount)

        elif command == 'SET_SELL_AMOUNT':
            #SET_SELL_AMOUNT,username,StockSymbol,amount
            SetSellAmount(RequestData_from_Client, transCount)

        elif command == 'SET_SELL_TRIGGER':
            #SET_SELL_TRIGGER,username,StockSymbol,amount
            SetSellTrigger(RequestData_from_Client, transCount)

        elif command == 'CANCEL_SET_SELL':
            #CANCEL_SET_SELL,username,StockSymbol
            CancelSetSell(RequestData_from_Client, transCount)

        elif command == 'DUMPLOG':
            #2 options here
            #DUMPLOG,username,filename
            #DUMPLOG,filename
            if len(RequestData_from_Client) == 2:
                Dumplog(RequestData_from_Client, transCount)
            else:
                DumplogUser(RequestData_from_Client, transCount)

        elif command == 'DISPLAY_SUMMARY':
            #DISPLAY_SUMMARY,username
            DisplaySummary(RequestData_from_Client, transCount)

        transCount += 1

        #Response_Transaction_Server = ConnectToTransactionServer(data)
        
        Reply = "Received"
        connection.sendall(str.encode(Reply))
    connection.close()


main()
