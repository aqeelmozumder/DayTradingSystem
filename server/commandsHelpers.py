import socket
import config
import pickle
import time
import db
import uuid
from yahoo_fin import stock_info as si

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
    db.newBuyOrder(username, stockSymbol, amount)
    return

def buyStock(buyOrder, username):
    # TODO
    #this may not be where/how we want to do this, but gives a good idea of what to do with the DB
    #need to send to transaction server and get quote from quote server, update user's "stocks" and balance
    stockSymbol : list
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
