from motor.motor_asyncio import AsyncIOMotorClient
import config

# Connect to MongoDB
client = AsyncIOMotorClient(config.MONGO_URL)
db = client.TomiokaGiyuDB

# --- Collections for your handlers ---

# 1. User Data (Used by: balance.py, pay.py, gen_gems.py, gen_dust.py)
users = db.users

# 2. Waifu Data (Used by: upload.py, spawn.py, gen_char.py)
characters = db.characters

# 3. Ownership Data (Used by: harem.py, trade.py, wredeem.py, grab.py)
claims = db.claims

# 4. Global Settings (Used by: mode.py, wmode.py)
settings = db.settings

# 5. Gift/Redeem Codes (Used by: gen_char.py, wredeem.py)
gift_codes = db.gift_codes
redeem_codes = db.gift_codes  # Add this so gen_dust.py can find it!

# 6. Trade Requests (Used by: trade.py - optional but keeps DB organized)
trades = db.trades

# 7. Waifu Mode / Spawn Configuration (Used by: wmode.py)
wmode = db.wmode

# Add this line to your database.py
staff = db.staff

groups = db.groups

shop_items = db['shop_items']

print("✅ MongoDB Connection Established and All 7 Collections Loaded!")