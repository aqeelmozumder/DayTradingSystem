import socket
import config
import pickle
import time
import pymongo
import db

def addFunds(username, amount):
    #increment user's balance by amount
    db.incrementBalance(username, round(float(amount), 2))
    return

def userBalance(username):
    user = db.findUser(username)
    return user["balance"]

def getStockPrice(stockSymbol):
    #this needs to get stock price from quote server
    #will just return dollar value of stock
    QuoteSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    QuoteSocket.connect(('quoteserver', config.QuoteServerPort))

    while True:
        QuoteSocket.send(pickle.dumps(stockSymbol))
        Response = QuoteSocket.recv(2048)
        QuoteSocket.close()
        if Response:
            break
  
    return pickle.loads(Response)

def insertBuyOrder(data):
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    db.newBuyOrder(username, stockSymbol, amount)
    return

def buyStock(buyOrder, username):
    # TODO
    #this may not be where/how we want to do this, but gives a good idea of what to do with the DB
    #need to send to transaction server and get quote from quote server, update user's "stocks" and balance
    
    stockSymbol = buyOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numberOfStocks = int(buyOrder["buyAmount"] / stockPrice)

    #ensure stock exists in users stocks
    if db.doesUserHaveStock(username, stockSymbol):
        #user has or previously had that stock, increment that stock's numberOfStock
        db.addNewStocks(username, stockSymbol, numberOfStocks)
    else:
        #user has not previously had that stock, add to stocks array
        db.addStocks(username, stockSymbol, numberOfStocks)
    #decrement user balance by (# of stock) * (stock price)
    addFunds(username, -round(float(numberOfStocks * stockPrice), 2))
    return

def getLastBuyOrder(username):
    user = db.findUser(username)
    if len(user["buyOrders"]) > 0:
        return user["buyOrders"][-1]
    else:
        return False

def removeLastBuyOrder(username):
    #remove last buy order from array of buy orders
    db.removeLastBuyOrder(username)
    return

def insertSellOrder(data):
    username = data[1]
    stockSymbol = data[2]
    amount = round(float(data[3]), 2)
    db.newSellOrder(username, stockSymbol, amount)
    return

def sellStock(sellOrder, username):
    #this may not be how/where we want to do here, but gives a good idea of what to do with the DB
    #need to send to transaction server, get quote from quote server, update user's "stocks" and balance

    stockSymbol = sellOrder["stockSymbol"]
    stockPrice = getStockPrice(stockSymbol)
    numberOfStocks = int(sellOrder["sellAmount"] / stockPrice)
    #ensure stock exists in user's stocks
    if db.doesUserHaveStock(username, stockSymbol):
        #decrement user's # of that stock
        db.removeStocks(username, stockSymbol, numberOfStocks)
    else:
        #error about not having the stock
        return
    depositToUser = round(float(numberOfStocks * stockPrice), 2)
    addFunds(username, round(float(numberOfStocks * stockPrice), 2))
    return

def getLastSellOrder(username):
    user = db.findUser(username)
    if len(user["sellOrders"]) > 0:
        return user["sellOrders"][-1]
    else:
        return False

def removeLastSellOrder(username):
    #remove last sell order from array of sell orders
    db.removeLastSellOrder(username)
    return
