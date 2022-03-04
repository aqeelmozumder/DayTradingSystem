import socket
import pickle
import config
import transactions
import commandsHelpers
import pymongo
import time
import db


# Connect To Quote Server
def ConnectToQuoteServer(data):
    QuoteSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    QuoteSocket.connect(('quoteserver', config.QuoteServerPort))

    while True:
        QuoteSocket.send(pickle.dumps(data))
        Response = QuoteSocket.recv(2048)
        QuoteSocket.close()
        if Response:
            break
  
    return pickle.loads(Response)   

def Add(data, transCount):
    #user, amount
    #add given amout to users account
    transactions.insertUserAndAmountTransaction(data, transCount)
    commandsHelpers.addFunds(data[1], data[2])
    return "Account balance updated"
    
def Quote(data, transCount):
    #user,StockSymbol
    #get current quote for the stock for specified user
    response_from_QuoteServer = ConnectToQuoteServer(data)
    data.append(response_from_QuoteServer[0])
    data.append(response_from_QuoteServer[3])
    data.append(response_from_QuoteServer[4])
    transactions.insertUserAndStockSymbolPriceTransaction(data, transCount)
    
    return ", ".join(str(item) for item in response_from_QuoteServer)
    
def Buy(data, transCount):
    #user,StockSymbol,amount
    #buy dollar amount of the stock for user at current price
    #users account must be greater or equal to amnt of purchase
    #user asked to confirm or cancel
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    if commandsHelpers.userBalance(data[1]) >= round(float(data[3]), 2):
        commandsHelpers.insertBuyOrder(data)
        return "Please chose commit or cancel your order"
    else:
        # need not enough funds error
        return "Insufficient balance"
    
def CommitBuy(data, transCount):
    #user
    #commits the most recently executed BUY command
    #user must have executed Buy within previous 60 secs
    #users cash account decrease by amount purchased
    #users account for given stock increased by purchase amount
    username = data[1]
    transactions.insertUserTransaction(data, transCount)
    buyOrder = commandsHelpers.getLastBuyOrder(username)
    if buyOrder:
        if (buyOrder["orderTime"] >= time.time() - 60):
            if commandsHelpers.userBalance(username) >= buyOrder["buyAmount"]:
                commandsHelpers.buyStock(buyOrder, username)
                return "BUY order completed"
            else:
                # error for not enough balance
                return "Insufficient balance"
        else:
            # error for 60 seconds having passed
            #return "No previous BUY order within 60S"
            pass
    return "No previous BUY order within 60S"
    
    
def CancelBuy(data, transCount):
    #user
    #cancels most recently executed BUY command
    #user must have executed Buy within previous 60 secs
    #last Buy command cancelled and any allocated system resourses reset and released
    username = data[1]
    transactions.insertUserTransaction(data, transCount)
    buyOrder = commandsHelpers.getLastBuyOrder(username)
    if buyOrder:
        if buyOrder["orderTime"] >= time.time() - 60:
            commandsHelpers.removeLastBuyOrder(username)
            return "BUY order cancelled"
        else:
            # error for 60 seconds having passed
            #return "No previous BUY order within 60S"
            pass
    return "No previous BUY order within 60S"
    
def Sell(data, transCount):
    #user, StockSymbol,amount
    #sell specified dollar amnt of the stock currently held by specified user
    #users acnt for stock must be greater or equal to amnt being sold
    #user asked to confirm or cancel
    # TODO checking if the user have that much amount of stock to sell 
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    if commandsHelpers.userBalance(data[1]) >= round(float(data[3]), 2):
        commandsHelpers.insertSellOrder(data)
        return "Please chose commit or cancel your order"
    else:
        # not enough stock error
        return "You do not have that much amount of stocks in your account"
    
def CommitSell(data, transCount):
    #user
    #cancels most recently executed SELL
    #user must have executed Sell within previous 60 secs
    #users account for given stock decremented by the sale amnt
    #the users cash acnt increased by sell amnt
    username = data[1]
    transactions.insertUserTransaction(data, transCount)
    sellOrder = commandsHelpers.getLastSellOrder(username)
    if sellOrder:
        if (sellOrder["orderTime"] >= time.time() - 60):
            if commandsHelpers.userBalance(username) >= sellOrder["sellAmount"]:
                commandsHelpers.sellStock(sellOrder, username)
                return "SELL order completed"
            else:
                # not enough stock error
                return "You do not have that much amount of stocks in your account"
        else:
            # error for 60 seconds having passed
            #return "No previous SELL order within 60S"
            pass
    return "No previous SELL order within 60S"
    
def CancelSell(data, transCount):
    #user
    #cancels most recently executed SELL, user must have executed Sell within previous 60 secs
    #last SELL command cancelled and any allocated system resourses reset and released
    username = data[1]
    transactions.insertUserTransaction(data, transCount)
    sellOrder = commandsHelpers.getLastSellOrder(username)
    if sellOrder:
        if sellOrder["orderTime"] >= time.time() - 60:
            commandsHelpers.removeLastSellOrder(username)
            return "SELL order cancelled"
        else:
            # error for 60 seconds having passed
            #return "No previous SELL order within 60S"
            pass
    else:
        # error for sell order not existing
        #return "No previous SELL order within 60S"
        pass
    return "No previous SELL order within 60S"

def SetBuyAmount(data, transCount):
    #user,StockSymbol,amount
    #sets defined amount of given stock to buy when the current stock price less or equal to BUY_TRIGGER
    #users cash acnt must be >= buy amnt at time transaction occurs
    #hold accnt created for the buy transaction to hold the specified amnt in reserve for when transaction triggered
    #users cash acnt decremented by specified amount
    #when trigger point reached the users stock account updated to reflect the BUY transaction
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    if commandsHelpers.userBalance(username) >= amount:
        if config.USER_COLLECTION.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0:
            #user has previous setBuy, set that setBuy amount to new value
            db.updateSetBuy(username, stockSymbol, amount)
        else:
            #user does not have a setBuy for that stock
            db.newSetBuy(username, stockSymbol, amount)

        #decrement user's balance by amount   
        commandsHelpers.addFunds(username, -amount)
        #increment holdBalance by amount
        db.incrementHoldBalance(username, amount)
        return "SET BUY for the given stock has been updated"
    else:
        # error for not enough funds
        return "Insufficient balance to create reserve account"
    return

def CancelSetBuy(data, transCount):
    #user,StockSymbol
    #cancels a SET_BUY command for given stock
    #must have been a SET_BUY command issued for given stock by user
    #all accounts are reset to values they would have had had the SET_BUY not been triggered
    #the BUY_TRIGGER for the given user and stock also cancelled
    username = data[1]
    stockSymbol = data[2]
    transactions.insertUserAndStockSymbolTransaction(data, transCount)
    if db.doesSetBuyExist(username, stockSymbol):
        db.removeSetBuy(username, stockSymbol)
        response = "The SET BUY for the given stock is removed\n"
    else:
        response = "No existing SET BUY for the given stock\n"
    if db.doesBuyTriggerExist(username, stockSymbol):
        # this also needs to decrement holdBalance
        db.removeBuyTrigger(username, stockSymbol)
        response += "The BUY TRIGGER for the given stock is removed"
    return response
    
def SetBuyTrigger(data, transCount):
    #user,StockSymbol,amount
    #Sets the trigger point base on the current stock price when any SET_BUY will execute
    #user must have specified a SET_BUY_AMOUNT prior to setting TRIGGER
    #set of the users buy triggers is updated to include the specified trigger
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = data[3]

    #check if setBuy exists for stock
    if db.doesSetBuyExist(username, stockSymbol):
        #check if already has trigger for stock
        if db.doesBuyTriggerExist(username, stockSymbol):
            #user has previous buy trigger for that stock, set that buy trigger amount to new value
            db.updateBuyTrigger(username, stockSymbol, amount)
        else:
            #user does not have a buy trigger for that stock
            db.newBuyTrigger(username, stockSymbol, amount)
        return "BUY TRIGGER for the given stock has been updated"
    else:
        #user does not have a setBuy for that stock
        # return error that they can't set buy trigger until have a set buy
        return "Make sure you already had SET BUY before setting BUY TRIGGER"
    return
    
def SetSellAmount(data, transCount):
    #user,StockSymbol,amount
    #sets defined amnt of stock to sell when current stock price equal or greater than sell trigger point
    #user must have the specified amnt of stock in their acnt for that stock
    #trigger init'd for user/stock combo, but not complete until SET_SELL_TRIGGER executed
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    stockPrice = commandsHelpers.getStockPrice(stockSymbol)
    amount = round(float(data[3]), 2)
    numStocksSellAmount = int(amount/stockPrice)
    #ensure user has stock
    if db.doesUserHaveStock(username, stockSymbol):
        if db.numberOfStockOwned(username, stockSymbol) >= numStocksSellAmount:
            if db.doesSetSellExist(username, stockSymbol):
                #user has previous setSell, set that setSell amount to new value
                db.updateSetSell(username, stockSymbol, amount)
            else:
                #user does not have a setSell for that stock
                db.newSetSell(username, stockSymbol, amount)
            return "SET SELL for the given stock has been updated"
        else:
            # error for not enough stocks for current value
            return "Do not have that amount of stocks in your account"
    else:
        # error for user not having that stock
        return "The given stock does not exist in your account"
    return
    
def SetSellTrigger(data, transCount):
    #user,StockSymbol,amount
    #sets stock price triffer point for executing any SET_SELL triggers associated with the given stock and user
    #user must have spec'd a SET_SELL_AMOUNT prior to SET_SELL_TRIGGER
    #reserve acnt created for spec'd amnt of stock
    #user acnt for stock reduced by max number of stocks that could be purchased
    #set of the users sell triggers is updated to include the specified trigger
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    #ensure user has stock
    if db.doesUserHaveStock(username, stockSymbol):
        #ensure user has set sell for that stock
        if db.doesSetSellExist(username, stockSymbol):
            if db.doesSellTriggerExist(username, stockSymbol):
                #user has previous sell trigger for that stock, set that sell trigger amount to new value
                db.updateSellTrigger(username, stockSymbol, amount)
            else:
                #user does not have a buy trigger for that stock
                db.newSellTrigger(username, stockSymbol, amount)

            numberOfStocks = int(commandsHelpers.getStockPrice(stockSymbol) * amount)
            #remove stocks from user stocks
            db.removeStocks(username, stockSymbol, numberOfStocks)
            #add stocks to user stocksHoldAccount
            if db.doesUserHaveStockInHold(username, stockSymbol):
                #user has previously had that stock, increment that stock's numberOfStock
                db.updateStockInHold(username, stockSymbol, numberOfStocks)
            else:
                #user has not previously had that stock, add to stocks array
                db.newStockInHold(username, stockSymbol, numberOfStocks)
            
            return "SELL TRIGGER for the given stock has been updated"
        else:
            #user does not have a setBell for that stock
            # return error that they can't set sell trigger until have a set buy
            return "Make sure you already had SET SELL before setting SELL TRIGGER"
    else:
        # error that user doens't have any of those stocks
        return "The given stock does not exist in your account"
    return
    
def CancelSetSell(data, transCount):
    #user,StockSymbol
    #cancels the SET_SELL associated with the stock and user
    #use must have had a previously set SET_SELL for stock
    #set of the users sell triggers is updated to remove the sell trigger associated with stock
    #all user acnt info reset to values would have been if SET_SELL had not been issued
    transactions.insertUserAndStockSymbolTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    if db.doesSetSellExist(username, stockSymbol):
        db.removeSetSell(username, stockSymbol)
        response = "The SET SELL for the given stock is removed\n"
    else:
        # add error for no set sell present for that stock
        response = "No existing SET SELL for the given stock\n" 
    if db.doesSellTriggerExist(username, stockSymbol):
        db.removeSellTrigger(username, stockSymbol)
        response += "The SELL TRIGGER for the given stock is removed"
    return response
    
def DumplogUser(data, transCount):
    #NOT IN FIRST LOG FILE
    #user,filename
    #print history of users transactions to the spec'd file
    transactions.insertUserAndFilenameTransaction(data, transCount)
    # set up dumplog for user
    userid = data[1]
    filename = data[2]

    f = open(filename, "w")
    f.write('<?xml version="1.0"?>\n')
    f.write("<log>\n")
    #print history of users transactions to the spec'd file

    logdata = config.USER_COLLECTION.find(
        { "username": userid },{"transactions":1, "_id": 0})
    logdata1 = logdata.next()

    for value in logdata1["transactions"]:
        if "type" in value:
            f.write("   <"+value["type"]+">\n")
        if  "timeStamp" in value:
            f.write('      <timestamp>'+ str(round(value["timeStamp"]))+'</timestamp>\n')
        if  "server" in value:
            f.write("      <server>"+str(value["server"])+"</server>\n")
        if "transactionNum" in value:
            f.write("      <transactionNum>"+str(value["transactionNum"])+"</transactionNum>\n")
        if "action" in value:
            f.write("      <action>"+str(value["action"])+"</action>\n")
        if "command" in value:
            f.write("      <command>"+str(value["command"])+"</command>\n")
        if "username" in value:
            f.write("      <username>"+str(value["username"])+"</username>\n")
        if "stockSymbol" in value:
            f.write("      <stockSymbol>"+str(value["stockSymbol"])+"</stockSymbol>\n")
        if "funds" in value:
            f.write("      <funds>"+str(value["funds"])+"</funds>\n")
        if "price" in value:
            f.write("      <price>"+str(value["stockPrice"])+"</price>\n")
        if "quoteServerTime" in value:
            f.write("      <quoteServerTime>"+str(value["quoteServerTime"])+"</quoteServerTime>\n")
        if "cryptokey" in value:
            f.write("      <cryptokey>"+str(value["cryptokey"])+"</cryptokey>\n")
        if "type" in value:
            f.write("   </"+str(value["type"])+">\n")
    f.write("</log>")
    f.close()

    return
    
def Dumplog(data, transCount):
    #filename
    #print to the spec'd file the complete set of transactions that have occured in system
    #can only be executed from the supervisor/root/admin account
    transactions.insertFilenameTransaction(data, transCount)
    filename = data[1]
    f = open(filename, "w")
    f.write('<?xml version="1.0"?>\n')
    f.write("<log>\n")
    #print history of users transactions to the spec'd file
    list_of_name = config.USER_COLLECTION.find({"username":{"$not":{"$eq":"ADMIN"}}},{"username":1,"_id":0})
    names = list_of_name.next()
    logdata = 0
    for name in names:
        if len(names) == 1:
            logdata = config.USER_COLLECTION.find(
                { "username": names[name] },{"transactions":1, "_id": 0})
        else:
            logdata = config.USER_COLLECTION.find(
                { "username": name["username"] },{"transactions":1, "_id": 0})
        logdata1 = logdata.next()

        for value in logdata1["transactions"]:
            if "type" in value:
                f.write("   <"+value["type"]+">\n")
            if  "timeStamp" in value:
                f.write('      <timestamp>'+ str(round(value["timeStamp"]))+'</timestamp>\n')
            if  "server" in value:
                f.write("      <server>"+str(value["server"])+"</server>\n")
            if "transactionNum" in value:
                f.write("      <transactionNum>"+str(value["transactionNum"])+"</transactionNum>\n")
            if "action" in value:
                f.write("      <action>"+str(value["action"])+"</action>\n")
            if "command" in value:
                f.write("      <command>"+str(value["command"])+"</command>\n")
            if "username" in value:
                f.write("      <username>"+str(value["username"])+"</username>\n")
            if "stockSymbol" in value:
                f.write("      <stockSymbol>"+str(value["stockSymbol"])+"</stockSymbol>\n")
            if "funds" in value:
                f.write("      <funds>"+str(value["funds"])+"</funds>\n")
            if "price" in value:
                f.write("      <price>"+str(value["price"])+"</price>\n")
            if "quoteServerTime" in value:
                f.write("      <quoteServerTime>"+str(value["quoteServerTime"])+"</quoteServerTime>\n")
            if "cryptokey" in value:
                f.write("      <cryptokey>"+str(value["cryptokey"])+"</cryptokey>\n")
            if "type" in value:
                f.write("   </"+str(value["type"])+">\n")
    f.write("</log>")
    f.close()
    # set up dumplog of all transactions
    # when we add admin users, only they can complete this transaction
    return
    
def DisplaySummary(data, transCount):
    #user
    #provides summary to client of the users transaction history and the current status of their accounts
    #as well as any set buy or sell triggers and their parameters
    transactions.insertUserTransaction(data, transCount)
    return
