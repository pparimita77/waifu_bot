import os
# --- BOT CREDENTIALS ---
# Get these from https://my.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "pirate_king_db"

# --- STAFF IDs ---
# Your Telegram User ID
OWNER_ID = [8325139144, 7987799736]

# List of Developer IDs (Who can use /rset, /add_sudo, etc.)
DEVS = [8325139144, 7987799736]

# List of Sudo IDs (Who can generate codes)
SUDOS = [7987799736, 8325139144]

# List of Uploader IDs (Who can add/delete characters)
UPLOADERS = [7987799736, 8325139144]

# --- CHANNEL LINKS ---
SUPPORT_CHAT = "Tomioka_Supportcore"
UPDATE_CHANNEL = "Tomioka_Giyu_Updatecore"
OWNER_USERNAME = "mnieuphoriasky"
DEV_USERNAME = "DemonKamadoTanjiro"

# --- GAME SETTINGS ---
SPAWN_MESSAGE_COUNT = 50  # Character spawns every 50 messages
DAILY_CLAIM_LIMIT = 1     # For normal users
PREMIUM_CLAIM_LIMIT = 3   # For premium users
DAILY_SLOT_LIMIT = 12      # Maximum slots for everyone
