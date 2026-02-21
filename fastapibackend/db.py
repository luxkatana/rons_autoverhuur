import pymongo
import dotenv
from os import environ

dotenv.load_dotenv()


dbclient = pymongo.AsyncMongoClient(environ["MONGODB_URI"])
database = dbclient.get_default_database()


autos = database.get_collection("autos")
authentication = database.get_collection("authentication")
usersdata = database.get_collection("usersdata")
