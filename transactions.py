import config
import time
import pymongo

def doesUserExist(username):
    return config.USER_COLLECTION.count_documents({ "username": username }) > 0

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
    config.USER_COLLECTION.insert_one(newUser)
    return

def insertExistingUserTransaction(username, newTransaction):
    newValues = {
        "$push":
            { "transactions": newTransaction } 
    }
    
    config.USER_COLLECTION.update_one({ "username": username }, newValues)
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
    #TODO update when we have admin users
    insertNewTransaction('ADMIN', newTransaction)
    return