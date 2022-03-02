import pymongo

CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
APP_DATABASE = CLIENT["seng468"]
USER_COLLECTION = APP_DATABASE["config.userCollection"]

QuoteServerHost = "127.0.0.1"
QuoteServerPort = 65438

TransactionServerHost = "127.0.0.1"
TransactionServerPort = 65433

WebServerHost = "127.0.0.1"
WebServerPort = 65432
