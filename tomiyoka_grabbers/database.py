from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client.tomioka_db

users = db.users
characters = db.characters
redeem_codes = db.codes