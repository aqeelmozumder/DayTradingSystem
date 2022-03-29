import pymongo


CLIENT = pymongo.MongoClient("mongodb://admin:admin@mongo:27017/seng468?authSource=admin")
# To run local:
# CLIENT = pymongo.MongoClient("mongodb://localhost:27017/") 
APP_DATABASE = CLIENT["seng468"]
USER_COLLECTION = APP_DATABASE["config.userCollection"]

QuoteServerHost = "0.0.0.0"
# To run local:
# QuoteContainerName = '0.0.0.0'
QuoteContainerName = 'quoteserver'
QuoteServerPort = 65438

WebServerHost = "0.0.0.0"
# To run local:
# WebContainerName = '0.0.0.0'
WebContainerName = 'webserver'
WebServerPort = 65432
