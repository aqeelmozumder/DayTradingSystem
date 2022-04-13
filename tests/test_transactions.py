import mongomock
import time
import uuid
from yahoo_fin import stock_info as si

client = mongomock.MongoClient()
app_database = client["seng468"]
user_collection = app_database["config.userCollection"]
username = 'coolUser'
transCountOne = 1

# pytest wasn't playing well with project modules, so just copying methods here

def doesUserExist(username):
    return user_collection.count_documents({ "username": username }) > 0

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
    user_collection.insert_one(newUser)
    return

def insertExistingUserTransaction(username, newTransaction):
    newValues = {
        "$push":
            { "transactions": newTransaction } 
    }
    user_collection.update_one({ "username": username }, newValues)
    return

def insertNewTransaction(username, newTransaction):
    if not doesUserExist(username):
        insertNewUserTransaction(username, newTransaction)
    else:
        insertExistingUserTransaction(username, newTransaction)
    return

def insertUserStockSymbolAndAmountTransaction(data, transCount):
    command = data[0]
    username = data[1]
    stockSymbol = data[2]
    amount = data[3]
    newTransaction = {
        "type": "userCommand",
        "timeStamp": time.time() * 1000,
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username,
        "stockSymbol": stockSymbol,
        "funds": round(float(amount), 2)
    }
    insertNewTransaction(username, newTransaction)
    return

def insertUserAndAmountTransaction(data, transCount):
    command = data[0]
    username = data[1]
    amount = data[2]
    newTransaction = {
        "type": "userCommand",
        "timeStamp": time.time() *1000,
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
        "type": "userCommand",
        "timeStamp": time.time() * 1000,
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "username": username,
        "stockSymbol": stockSymbol
    }
    insertNewTransaction(username, newTransaction)
    return

def insertUserTransaction(data, transCount):
    command = data[0]
    username = data[1]
    newTransaction = {
        "type": "userCommand",
        "timeStamp": time.time() *1000,
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
        "type": "userCommand",
        "timeStamp": time.time()*1000,
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
        "type": "userCommand",
        "timeStamp": time.time()*1000,
        "server": "WebServer",
        "transactionNum": transCount,
        "command": command,
        "filename": filename
    }
    insertNewTransaction('ADMIN', newTransaction)
    return

def updateSetBuy(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username, "setBuy.stockSymbol": stockSymbol },
        { "$set": { "setBuy.$.amount": amount } },
        upsert=True
    )
    return

def newSetBuy(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username },
        { "$addToSet": { "setBuy": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def incrementHoldBalance(username, amount):
    user_collection.update_one(
        { "username": username },
        { "$inc": { "holdBalance": amount } }
    )
    return

def doesSetBuyExist(username, stockSymbol):
    return user_collection.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0

def removeSetBuy(username, stockSymbol):
    user_collection.update_one(
        { "username": username },
        { "$pull": { "setBuy": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def doesBuyTriggerExist(username, stockSymbol):
    return user_collection.count_documents({ "username": username, "buyTriggers.stockSymbol": stockSymbol }) > 0

def removeBuyTrigger(username, stockSymbol):
    user_collection.update_one(
        { "username": username },
        { "$pull": { "buyTriggers": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def updateBuyTrigger(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username, "buyTriggers.stockSymbol": stockSymbol },
        { "$set": { "buyTriggers.$.amount": amount } },
        upsert=True
    )
    return

def newBuyTrigger(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username },
        { "$addToSet": { "buyTrigger": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def doesUserHaveStock(username, stockSymbol):
    return user_collection.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0

def numberOfStockOwned(username, stockSymbol):
    userStockInfo = user_collection.find_one({ "username": username, "stocks.stockSymbol": stockSymbol })["stocks"]
    stockInfo = next((x for x in userStockInfo if x["stockSymbol"] == stockSymbol), None)
    return stockInfo["numberOfStock"]

def doesSetSellExist(username, stockSymbol):
    return user_collection.count_documents({ "username": username, "setSell.stockSymbol": stockSymbol }) > 0

def updateSetSell(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username, "setSell.stockSymbol": stockSymbol },
        { "$set": { "setSell.$.amount": amount } },
        upsert=True
    )
    return

def newSetSell(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username },
        { "$addToSet": { "setSell": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def doesSellTriggerExist(username, stockSymbol):
    return user_collection.count_documents({ "username": username, "sellTriggers.stockSymbol": stockSymbol }) > 0

def updateSellTrigger(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username, "sellTriggers.stockSymbol": stockSymbol },
        { "$set": { "sellTriggers.$.amount": amount } },
        upsert=True
    )
    return

def newSellTrigger(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username },
        { "$addToSet": { "sellTrigger": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def doesUserHaveStockInHold(username, stockSymbol):
    return user_collection.count_documents({ "username": username, "stocksHoldAccount.stockSymbol": stockSymbol }) > 0

def updateStockInHold(username, stockSymbol, numberOfStocks):
    user_collection.update_one(
        { "username": username, "stocksHoldAccount.stockSymbol": stockSymbol },
        { "$inc": { "stocksHoldAccount.$.numberOfStock": numberOfStocks } },
        upsert=True
    )
    return

def newStockInHold(username, stockSymbol, numberOfStocks):
    user_collection.update_one(
        { "username": username },
        { "$addToSet": { "stocksHoldAccount": { "stockSymbol": stockSymbol, "numberOfStock": numberOfStocks } } },
    )
    return

def removeSetSell(username, stockSymbol):
    user_collection.update_one(
        { "username": username },
        { "$pull": { "setSell": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def removeSellTrigger(username, stockSymbol):
    user_collection.update_one(
        { "username": username },
        { "$pull": { "sellTriggers": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def removeStocks(username, stockSymbol, numberOfStocks):
    user_collection.update_one(
        { "username": username, "stocks.stockSymbol": stockSymbol },
        { "$inc": { "stocks.$.numberOfStock": -numberOfStocks } }
    )
    return

def addNewStocks(username, stockSymbol, numberOfStocks):
    user_collection.update_one(
        { "username": username, "stocks.stockSymbol": stockSymbol },
        { "$inc": { "stocks.$.numberOfStock": numberOfStocks } },
        upsert=True
    )
    return

def addStocks(username, stockSymbol, numberOfStocks):
    user_collection.update_one(
        { "username": username },
        { "$addToSet": { "stocks": { "stockSymbol": stockSymbol, "numberOfStock": numberOfStocks } } },
    )
    return

def incrementBalance(username, amount):
    user_collection.update_one(
        { "username": username },
        { "$inc": { "balance": amount } }
    )
    return

def findUser(username):
    return user_collection.find_one({ "username": username })

def newBuyOrder(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username },
        { "$push": {
            "buyOrders": {
                "buyAmount": amount,
                "stockSymbol": stockSymbol,
                "orderTime": time.time()
            }
        } }
    )
    return

def removeLastBuyOrder(username):
    user_collection.update_one({ "username": username }, { "$pop": { "buyOrders": 1 } })
    return

def removeLastSellOrder(username):
    user_collection.update_one({ "username": username }, { "$pop": { "sellOrders": 1 } })
    return

def newSellOrder(username, stockSymbol, amount):
    user_collection.update_one(
        { "username": username },
        { "$push": {
            "sellOrders": {
                "sellAmount": amount,
                "stockSymbol": stockSymbol,
                "orderTime": time.time()
            }
        } }
    )
    return

def addFunds(username, amount):
    incrementBalance(username, round(float(amount), 2))
    return

def userBalance(username):
    user = findUser(username)
    return user["balance"]

def getStockPrice(stockSymbol):
    receive_from_web = stockSymbol

    if len(receive_from_web) > 1 and type(receive_from_web) == list:
        stockSymbol = receive_from_web[2]
        try:
            quoteprice = round(si.get_live_price(stockSymbol), 2)
        except:
            quoteprice = 0
        username = receive_from_web[1]
        timestamp = time.time() * 1000
        cryptokey = str(uuid.uuid1())

        return [quoteprice, stockSymbol, username, timestamp, cryptokey]
    elif len(receive_from_web) == 1 or type(receive_from_web) == str:
        try:
            result = round(si.get_live_price(receive_from_web), 2)
            return result
        except:
            return 0
    else:
        return "Missing parameters"

def insertBuyOrder(data):
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    newBuyOrder(username, stockSymbol, amount)
    return

def buyStock(buyOrder, username):
    stockSymbol : list
    stockSymbol = buyOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numberOfStocks = int(buyOrder["buyAmount"] / stockPrice)
    if doesUserHaveStock(username, stockSymbol):
        addNewStocks(username, stockSymbol, numberOfStocks)
    else:
        addStocks(username, stockSymbol, numberOfStocks)
    addFunds(username, -round(float(numberOfStocks * stockPrice), 2))
    return

def getLastBuyOrder(username):
    user = findUser(username)
    if len(user["buyOrders"]) > 0:
        return user["buyOrders"][-1]
    else:
        return False

def insertSellOrder(data):
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    newSellOrder(username, stockSymbol, amount)
    return

def sellStock(sellOrder, username):
    stockSymbol = sellOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numberOfStocks = int(sellOrder["sellAmount"] / stockPrice)
    if doesUserHaveStock(username, stockSymbol):
        removeStocks(username, stockSymbol, numberOfStocks)
    else:
        return
    depositToUser = round(float(numberOfStocks * stockPrice), 2)
    addFunds(username, round(float(numberOfStocks * stockPrice), 2))
    return

def getLastSellOrder(username):
    user = findUser(username)
    if len(user["sellOrders"]) > 0:
        return user["sellOrders"][-1]
    else:
        return False

def init_user():
    newUser = {
        "username": username,
        "transactions": [],
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
    user_collection.insert_one(newUser)
    
def clear_collection():
    user_collection.delete_many({})
    
def test_doesUserExist():
    clear_collection()
    output = user_collection.count_documents({ "username": username }) > 0
    assert output == False
    init_user()
    output = user_collection.count_documents({ "username": username }) > 0
    assert output == True

def Add(data, transCount):
    insertUserAndAmountTransaction(data, transCount)
    addFunds(data[1], data[2])
    return "Account balance updated"

def test_Add():
    clear_collection()
    init_user()
    initialBalance = userBalance(username)
    assert initialBalance == 0
    command = 'ADD'
    amount = 100
    data = [command, username, amount]
    message = Add(data, transCountOne)
    finalBalance = userBalance(username)
    assert finalBalance == amount
    assert message == "Account balance updated"

def Buy(data, transCount):
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    if userBalance(data[1]) >= round(float(data[3]), 2):
        insertBuyOrder(data)
        return "Please chose commit or cancel your order"
    else:
        return "Insufficient balance"
    
def test_Buy():
    clear_collection()
    init_user()
    command = 'BUY'
    stock = 'GME'
    amount = 100
    data = [command, username, stock, amount]
    # user has no funds,  should fail
    message = Buy(data, transCountOne)
    assert message ==  "Insufficient balance"
    addFunds(username, 200)
    # user now has funds, should pass
    message = Buy(data, transCountOne)
    assert message ==  "Please chose commit or cancel your order"
    
def CancelBuy(data, transCount):
    username = data[1]
    insertUserTransaction(data, transCount)
    buyOrder = getLastBuyOrder(username)
    if buyOrder:
        if buyOrder["orderTime"] >= time.time() - 60:
            removeLastBuyOrder(username)
            return "BUY order cancelled"
        else:
            pass
    return "No previous BUY order within 60S"

def test_CancelBuy():
    clear_collection()
    init_user()
    command = 'CANCEL_BUY'
    data = [command, username]
    stock = 'GME'
    amount = 100
    dataBuy = ['BUY', username, stock, amount]
    addFunds(username, 200)
    # No buy, should fail
    message = CancelBuy(data, transCountOne)
    assert message == "No previous BUY order within 60S"
    Buy(dataBuy, transCountOne)
    # There is now a buy, should cancel
    message = CancelBuy(data, transCountOne)
    assert message == "BUY order cancelled"
    # buy should be removed, should fail
    message = CancelBuy(data, transCountOne)
    assert message == "No previous BUY order within 60S"

def Sell(data, transCount):
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    if userBalance(data[1]) >= round(float(data[3]), 2):
        insertSellOrder(data)
        return "Please chose commit or cancel your order"
    else:
        return "You do not have that much amount of stocks in your account"

def test_Sell():
    clear_collection()
    init_user()
    command = 'SELL'
    stock = 'GME'
    amount = 100
    data = [command, username, stock, amount]
    message = Sell(data, transCountOne)
    assert message == "You do not have that much amount of stocks in your account"
    addFunds(username, 200)
    message = Sell(data, transCountOne)
    assert message == "Please chose commit or cancel your order"

def SetBuyAmount(data, transCount):
    insertUserStockSymbolAndAmountTransaction(data, transCount)
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    if userBalance(username) >= amount:
        if user_collection.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0:
            updateSetBuy(username, stockSymbol, amount)
        else:
            newSetBuy(username, stockSymbol, amount)
        addFunds(username, -amount)
        incrementHoldBalance(username, amount)
        return "SET BUY for the given stock has been updated"
    else:
        return "Insufficient balance to create reserve account"

def test_SetBuyAmount():
    clear_collection()
    init_user()
    command = 'SET_BUY'
    stock = 'GME'
    amount = 100
    data = [command, username, stock, amount]
    message = SetBuyAmount(data, transCountOne)
    assert message == "Insufficient balance to create reserve account"
    addFunds(username, 400)
    message = SetBuyAmount(data, transCountOne)
    assert message == "SET BUY for the given stock has been updated"
    data[3] = amount + 50
    message = SetBuyAmount(data, transCountOne)
    assert message == "SET BUY for the given stock has been updated"

def CancelSetBuy(data, transCount):
    username = data[1]
    stockSymbol = data[2]
    insertUserAndStockSymbolTransaction(data, transCount)
    if doesSetBuyExist(username, stockSymbol):
        removeSetBuy(username, stockSymbol)
        response = "The SET BUY for the given stock is removed\n"
    else:
        response = "No existing SET BUY for the given stock\n"
    if doesBuyTriggerExist(username, stockSymbol):
        # this also needs to decrement holdBalance
        removeBuyTrigger(username, stockSymbol)
        response += "The BUY TRIGGER for the given stock is removed"
    return response

def test_CancelSetBuy():
    clear_collection()
    init_user()
    command = 'SET_BUY'
    stock = 'GME'
    amount = 100
    data = [command, username, stock, amount]
    dataCancel = ['CANCEL_SET_BUY', username, stock]
    message = CancelSetBuy(dataCancel, transCountOne)
    assert message == "No existing SET BUY for the given stock\n"
    addFunds(username, 400)
    message = SetBuyAmount(data, transCountOne)
    assert message == "SET BUY for the given stock has been updated"
    message = CancelSetBuy(dataCancel, transCountOne)
    assert message == "The SET BUY for the given stock is removed\n"
    