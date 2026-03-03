# economy.py
from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.waifu_bot

def get_user(user_id):
    return db.users.find_one({"user_id": user_id})

def add_user(user_id):
    if not get_user(user_id):
        db.users.insert_one({
            "user_id": user_id,
            "gems": 0,
            "stardust": 0,
            "emerald": 0,
            "collection": [],
            "favorites": [],
            "last_claim": None,
            "daily_streak": 0,
        })

def add_gems(user_id, amount):
    add_user(user_id)
    db.users.update_one({"user_id": user_id}, {"$inc": {"gems": amount}})

def add_stardust(user_id, amount):
    add_user(user_id)
    db.users.update_one({"user_id": user_id}, {"$inc": {"stardust": amount}})

def add_emerald(user_id, amount):
    add_user(user_id)
    db.users.update_one({"user_id": user_id}, {"$inc": {"emerald": amount}})

def update_last_claim(user_id, timestamp):
    db.users.update_one({"user_id": user_id}, {"$set": {"last_claim": timestamp}})

def get_balance(user_id):
    add_user(user_id)
    user = get_user(user_id)
    return user.get("gems", 0), user.get("stardust", 0), user.get("emerald", 0)
