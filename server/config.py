import pymongo

CLIENT = pymongo.MongoClient("mongodb://admin:admin@mongo:27017/seng468?authSource=admin")
# To run local:
# CLIENT = pymongo.MongoClient("mongodb://localhost:27017/") 
APP_DATABASE = CLIENT["seng468"]
USER_COLLECTION = APP_DATABASE["config.userCollection"]


WebServerHost = "0.0.0.0"
# To run local:
# WebContainerName = '0.0.0.0'
WebContainerName = 'seng468_webserver_1'
WebServerPort = 65432
