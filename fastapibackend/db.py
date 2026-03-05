import pymongo
import dotenv
import warnings
from os import environ

dotenv.load_dotenv()


dbclient = pymongo.AsyncMongoClient(environ["MONGODB_URI"])
database = dbclient.get_default_database()


cars = database.get_collection("autos")
authentication = database.get_collection("authentication")
usersdata = database.get_collection("usersdata")
payments_status = database.get_collection("payments_status")

db_vosverhuur_client = pymongo.AsyncMongoClient(environ["VOS_AUTOVERHUUR_URI"])

vosautos = db_vosverhuur_client.get_default_database().get_collection("statictestdata")
if vosautos.name == "statictestdata":
    warnings.warn(
        "WARNING: still using testing statictestdata, change it ASAP in db.py and .env file"
    )
