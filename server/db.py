import config
import transactions
import commandsHelpers
import pymongo
import time

CLIENT = pymongo.MongoClient("mongodb://admin:admin@mongo:27017/seng468?authSource=admin")
APP_DATABASE = CLIENT["seng468"]
USER_COLLECTION = APP_DATABASE["config.userCollection"]

def updateSetBuy(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username, "setBuy.stockSymbol": stockSymbol },
        { "$set": { "setBuy.$.amount": amount } },
        upsert=True
    )
    return

def newSetBuy(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$addToSet": { "setBuy": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def incrementHoldBalance(username, amount):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$inc": { "holdBalance": amount } }
    )
    return

def doesSetBuyExist(username, stockSymbol):
    return USER_COLLECTION.count_documents({ "username": username, "setBuy.stockSymbol": stockSymbol }) > 0

def removeSetBuy(username, stockSymbol):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$pull": { "setBuy": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def doesBuyTriggerExist(username, stockSymbol):
    return USER_COLLECTION.count_documents({ "username": username, "buyTriggers.stockSymbol": stockSymbol }) > 0

def removeBuyTrigger(username, stockSymbol):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$pull": { "buyTriggers": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def updateBuyTrigger(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username, "buyTriggers.stockSymbol": stockSymbol },
        { "$set": { "buyTriggers.$.amount": amount } },
        upsert=True
    )
    return

def newBuyTrigger(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$addToSet": { "buyTrigger": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def doesUserHaveStock(username, stockSymbol):
    return USER_COLLECTION.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0

def numberOfStockOwned(username, stockSymbol):
    userStockInfo = config.USER_COLLECTION.find_one({ "username": username, "stocks.stockSymbol": stockSymbol })["stocks"]
    stockInfo = next((x for x in userStockInfo if x["stockSymbol"] == stockSymbol), None)
    return stockInfo["numberOfStock"]

def doesSetSellExist(username, stockSymbol):
    return USER_COLLECTION.count_documents({ "username": username, "setSell.stockSymbol": stockSymbol }) > 0

def updateSetSell(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username, "setSell.stockSymbol": stockSymbol },
        { "$set": { "setSell.$.amount": amount } },
        upsert=True
    )
    return

def newSetSell(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$addToSet": { "setSell": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def doesSellTriggerExist(username, stockSymbol):
    return USER_COLLECTION.count_documents({ "username": username, "sellTriggers.stockSymbol": stockSymbol }) > 0


def updateSellTrigger(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username, "sellTriggers.stockSymbol": stockSymbol },
        { "$set": { "sellTriggers.$.amount": amount } },
        upsert=True
    )
    return

def newSellTrigger(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$addToSet": { "sellTrigger": { "stockSymbol": stockSymbol, "amount": amount } } },
    )
    return

def doesUserHaveStockInHold(username, stockSymbol):
    return USER_COLLECTION.count_documents({ "username": username, "stocksHoldAccount.stockSymbol": stockSymbol }) > 0

def updateStockInHold(username, stockSymbol, numberOfStocks):
    USER_COLLECTION.update_one(
        { "username": username, "stocksHoldAccount.stockSymbol": stockSymbol },
        { "$inc": { "stocksHoldAccount.$.numberOfStock": numberOfStocks } },
        upsert=True
    )
    return

def newStockInHold(username, stockSymbol, numberOfStocks):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$addToSet": { "stocksHoldAccount": { "stockSymbol": stockSymbol, "numberOfStock": numberOfStocks } } },
    )
    return

def removeSetSell(username, stockSymbol):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$pull": { "setSell": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def removeSellTrigger(username, stockSymbol):
    config.USER_COLLECTION.update_one(
        { "username": username },
        { "$pull": { "sellTriggers": { "$elemMatch": { "stockSymbol": stockSymbol } } } }
    )
    return

def removeStocks(username, stockSymbol, numberOfStocks):
    USER_COLLECTION.update_one(
        { "username": username, "stocks.stockSymbol": stockSymbol },
        { "$inc": { "stocks.$.numberOfStock": -numberOfStocks } }
    )
    return

def addNewStocks(username, stockSymbol, numberOfStocks):
    USER_COLLECTION.update_one(
        { "username": username, "stocks.stockSymbol": stockSymbol },
        { "$inc": { "stocks.$.numberOfStock": numberOfStocks } },
        upsert=True
    )
    return

def addStocks(username, stockSymbol, numberOfStocks):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$addToSet": { "stocks": { "stockSymbol": stockSymbol, "numberOfStock": numberOfStocks } } },
    )
    return

def incrementBalance(username, amount):
    USER_COLLECTION.update_one(
        { "username": username },
        { "$inc": { "balance": amount } }
    )
    return

def findUser(username):
    return USER_COLLECTION.find_one({ "username": username })

def newBuyOrder(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
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
    USER_COLLECTION.update_one({ "username": username }, { "$pop": { "buyOrders": 1 } })
    return

def removeLastSellOrder(username):
    USER_COLLECTION.update_one({ "username": username }, { "$pop": { "sellOrders": 1 } })
    return

def newSellOrder(username, stockSymbol, amount):
    USER_COLLECTION.update_one(
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

