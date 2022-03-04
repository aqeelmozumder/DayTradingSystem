import pymongo

CLIENT = pymongo.MongoClient("mongodb://mongo:27017")
APP_DATABASE = CLIENT["seng468"]
USER_COLLECTION = APP_DATABASE["config.userCollection"]

QuoteServerHost = "0.0.0.0"
QuoteServerPort = 65438

WebServerHost = "0.0.0.0"
WebServerPort = 65432
