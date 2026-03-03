from motor.motor_asyncio import AsyncIOMotorClient
import config

# Connect to MongoDB
client = AsyncIOMotorClient(config.MONGO_URL)

# This line was causing the error, now it will work:
db = client["TomiokaBotDB"]

# Collections
users = db.users
characters = db.characters
claims = db.claims
settings = db.settings
gift_codes = db.gift_codes
trades = db.trades
wmode = db.wmode
staff = db['staff']          # <--- Make sure this line is exactly like this
groups = db.groups
shop_items = db['shop_items'] # <--- Fix for your previous error too
chat_settings = db.chat_settings
shop_config = db.shop_config

# --- Helper: Universal User Fetch ---
async def get_user(user_id):
    return await users.find_one({"$or": [{"_id": user_id}, {"user_id": user_id}]})

# --- Rarity Lock Functions (Add these to database.py) ---

async def get_disabled_claims():
    doc = await settings.find_one({"_id": "claim_rarity_lock"})
    if doc:
        return doc.get("disabled", [])
    return []

async def toggle_claim_rarity(rarity):
    """Owner function to switch a rarity between Locked and Unlocked."""
    data = await settings.find_one({"_id": "claim_rarity_lock"})
    disabled = data.get("disabled", []) if data else []
    
    if rarity in disabled:
        disabled.remove(rarity)
    else:
        disabled.append(rarity)
        
    await settings.update_one(
        {"_id": "claim_rarity_lock"}, 
        {"$set": {"disabled": disabled}}, 
        upsert=True
    )
    return disabled
    
async def get_enabled_spawn_rarities():
    """Fetches the whitelist of rarities from the /rarity command"""
    data = await settings.find_one({"_id": "global_spawn_settings"})
    if not data or "rarities" not in data:
        # If nothing is set, default to all standard rarities
        return ["Common", "Legendary", "Rare", "Special", "Limited", "Celestial", 
                "Manga", "Expensive", "Giveaway", "Royal", "Summer", "Winter", 
                "Valentine", "Seasonal", "Halloween", "Christmas", "AMV"]
    return data["rarities"]
    
# --- Premium Logic ---
async def set_premium(user_id, days):
    expiry_date = datetime.now() + timedelta(days=days)
    await users.update_one(
        {"$or": [{"_id": user_id}, {"user_id": user_id}]},
        {"$set": {"is_premium": True, "premium_expiry": expiry_date, "user_id": user_id}},
        upsert=True
    )
    return expiry_date

async def is_user_premium(user_id):
    user_data = await get_user(user_id)
    if not user_data or not user_data.get("is_premium"):
        return False
    
    expiry = user_data.get("premium_expiry")
    if expiry and expiry < datetime.now():
        await users.update_one(
            {"$or": [{"_id": user_id}, {"user_id": user_id}]}, 
            {"$set": {"is_premium": False}}
        )
        return False
    return True

# --- EXP & Leveling Logic ---
async def add_exp(user_id, amount):
    user_data = await get_user(user_id)
    if not user_data:
        user_data = {"is_premium": False, "exp": 0, "level": 0}
        
    if user_data.get("is_premium"):
        amount *= 2

    await users.update_one(
        {"$or": [{"_id": user_id}, {"user_id": user_id}]},
        {"$inc": {"exp": amount}, "$set": {"user_id": user_id}},
        upsert=True
    )
    
    updated_user = await get_user(user_id)
    new_level = updated_user.get("exp", 0) // 1000 
    if new_level > updated_user.get("level", 0):
        await users.update_one(
            {"$or": [{"_id": user_id}, {"user_id": user_id}]}, 
            {"$set": {"level": new_level}}
        )
        return True, new_level
    return False, updated_user.get("level", 0)