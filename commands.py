import config
import transactions
import commandsHelpers
import pymongo
import time
import db

def Add(data, transCount):
    #user, amount
    #add given amout to users account
    transactions.insertUserAndAmountTransaction(data, transCount)
    commandsHelpers.addFunds(data[1], data[2])
    return
    
def Quote(data, transCount):
    #user,StockSymbol
    #get current quote for the stock for specified user
    transactions.insertUserAndStockSymbolTransaction(data, transCount)
    #TODO need more here on interaction with quote server
    return
    
def Buy(data, transCount):
    #user,StockSymbol,amount
    #buy dollar amount of the stock for user at current price
    #users account must be greater or equal to amnt of purchase
    #user asked to confirm or cancel
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    if commandsHelpers.userBalance(data[1]) >= round(float(data[3]), 2):
        commandsHelpers.insertBuyOrder(data)
        return
    else:
        #TODO need not enough funds error
        return
    return
    
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
            else:
                #TODO error for not enough balance
                return
        else:
            #TODO error for 60 seconds having passed
            return
    return
    
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
        else:
            #TODO error for 60 seconds having passed
            return
    return
    
def Sell(data, transCount):
    #user, StockSymbol,amount
    #sell specified dollar amnt of the stock currently held by specified user
    #users acnt for stock must be greater or equal to amnt being sold
    #user asked to confirm or cancel
    transactions.insertUserStockSymbolAndAmountTransaction(data, transCount)
    if commandsHelpers.userBalance(data[1]) >= round(float(data[3]), 2):
        commandsHelpers.insertSellOrder(data)
        return
    else:
        #TODO need not enough funds error
        return
    return
    
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
            else:
                #TODO error for not enough balance
                return
        else:
            #TODO error for 60 seconds having passed
            return
    return
    
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
        else:
            #TODO error for 60 seconds having passed
            return
    else:
        #TODO error for sell order not existing
        return
    return

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
    else:
        #TODO error for not enough funds
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
    transactions.insertUserAndStockSymbolTransaction(data, transCount)
    if db.doesSetBuyExist(username, stockSymbol):
        db.removeSetBuy(username, stockSymbol)
    else:
        #TODO
        pass
    if db.doesBuyTriggerExist(username, stockSymbol):
        db.removeBuyTrigger(username, stockSymbol)
    #TODO this also needs to decrement holdBalance
    return
    
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
    if doesSetBuyExist(username, stockSymbol):
        #check if already has trigger for stock
        if db.doesBuyTriggerExist(username, stockSymbol):
            #user has previous buy trigger for that stock, set that buy trigger amount to new value
            db.updateBuyTrigger(username, stockSymbol, amount)
        else:
            #user does not have a buy trigger for that stock
            db.newBuyTrigger(username, stockSymbol, amount)
    else:
        #user does not have a setBuy for that stock
        #TODO return error that they can't set buy trigger until have a set buy
        return
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
        else:
            #TODO error for not enough stocks for current value
            return
    else:
        #TODO error for user not having that stock
        return
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
        else:
            #user does not have a setBell for that stock
            #TODO return error that they can't set sell trigger until have a set buy
            return
    else:
        #TODO error that user doens't have any of those stocks
        return
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
    else:
        #TODO add error for no set sell present for that stock
        pass
    if db.doesSellTriggerExist(username, stockSymbol):
        db.removeSellTrigger(username, stockSymbol)
    return
    
def DumplogUser(data, transCount):
    #NOT IN FIRST LOG FILE
    #user,filename
    #print history of users transactions to the spec'd file
    transactions.insertUserAndFilenameTransaction(data, transCount)
    #TODO set up dumplog for user
    return
    
def Dumplog(data, transCount):
    #filename
    #print to the spec'd file the complete set of transactions that have occured in system
    #can only be executed from the supervisor/root/admin account
    transactions.insertFilenameTransaction(data, transCount)
    #TODO set up dumplog of all transactions
    #TODO when we add admin users, only they can complete this transaction
    return
    
def DisplaySummary(data, transCount):
    #user
    #provides summary to client of the users transaction history and the current status of their accounts
    #as well as any set buy or sell triggers and their parameters
    transactions.insertUserTransaction(data, transCount)
    return
