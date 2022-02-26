import config
import time
import pymongo

def addFunds(username, amount):
    #increment user's balance by amount
    config.USER_COLLECTION.update_one(
        { "username": username },
        { "$inc": { "balance": round(float(amount), 2) } }
    )
    return

def userBalance(username):
    user = config.USER_COLLECTION.find_one({ "username": username })
    return user["balance"]

def getStockPrice(stockSymbol):
    # TODO
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
    config.USER_COLLECTION.update_one({ "username": username }, newOrderItem)
    return

def buyStock(buyOrder, username):
    # TODO
    #this may not be where/how we want to do this, but gives a good idea of what to do with the DB
    #need to send to transaction server and get quote from quote server, update user's "stocks" and balance
    
    stockSymbol = buyOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numStockBuy = int(buyOrder["buyAmount"] / stockPrice)

    #ensure stock exists in users stocks
    if config.USER_COLLECTION.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0:
        #user has or previously had that stock, increment that stock's numberOfStock
        config.USER_COLLECTION.update_one(
            { "username": username, "stocks.stockSymbol": stockSymbol },
            { "$inc": { "stocks.$.numberOfStock": numStockBuy } },
            upsert=True
        )
    else:
        #user has not previously had that stock, add to stocks array
        config.USER_COLLECTION.update_one(
            { "username": username },
            { "$addToSet": { "stocks": { "stockSymbol": stockSymbol, "numberOfStock": numStockBuy } } },
        )
    #decrement user balance by (# of stock) * (stock price)
    addFunds(username, -round(float(numStockBuy * stockPrice), 2))
    return

def getLastBuyOrder(username):
    user = config.USER_COLLECTION.find_one({ "username": username })
    if len(user["buyOrders"]) > 0:
        return user["buyOrders"][-1]
    else:
        return False

def removeLastBuyOrder(username):
    #remove last buy order from array of buy orders
    config.USER_COLLECTION.update_one({ "username": username }, { "$pop": { "buyOrders": 1 } })
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
    config.USER_COLLECTION.update_one({ "username": username }, newOrderItem)
    return

def sellStock(sellOrder, username):
    #this may not be how/where we want to do here, but gives a good idea of what to do with the DB
    #need to send to transaction server, get quote from quote server, update user's "stocks" and balance

    stockSymbol = sellOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numStockSell = int(sellOrder["sellAmount"] / stockPrice)
    #ensure stock exists in user's stocks
    if config.USER_COLLECTION.count_documents({ "username": username, "stocks.stockSymbol": stockSymbol }) > 0:
        #decrement user's # of that stock
        config.USER_COLLECTION.update_one(
            { "username": username, "stocks.stockSymbol": stockSymbol },
            { "$inc": { "stocks.$.numberOfStock": -numStockSell } },
            upsert=True
        )
    else:
        #error about not having the stock
        return
    depositToUser = round(float(numStockSell * stockPrice), 2)
    addFunds(username, round(float(numStockSell * stockPrice), 2))
    return

def getLastSellOrder(username):
    user = config.USER_COLLECTION.find_one({ "username": username })
    if len(user["sellOrders"]) > 0:
        return user["sellOrders"][-1]
    else:
        return False

def removeLastSellOrder(username):
    #remove last sell order from array of sell orders
    config.USER_COLLECTION.update_one({ "username": username }, { "$pop": { "sellOrders": 1 } })
    return
