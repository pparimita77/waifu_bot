import random
import string
from pyrogram import Client, filters
from config import OWNER_ID, DEVS
from database import db, characters

gift_codes = db.gift_codes

# This creates a clean, flat list of all authorized IDs
def get_auth_users():
    auth = []
    # Add Owner(s)
    if isinstance(OWNER_ID, list):
        auth.extend(OWNER_ID)
    else:
        auth.append(OWNER_ID)
    # Add Devs
    if DEVS:
        if isinstance(DEVS, list):
            auth.extend(DEVS)
        else:
            auth.append(DEVS)
    return list(set(auth)) # set() removes any accidental duplicates

AUTHORIZED_USERS = get_auth_users()

@Client.on_message(filters.command("gen_char") & filters.user(AUTHORIZED_USERS))
async def generate_redeem_code(client, message):
    # Format: /gen_char <char_id> <usage>
    if len(message.command) < 3:
        return await message.reply_text("🌊 **Usᴀɢᴇ:** `/gen_char <char_id> <usage>`\nEx: `/gen_char 101 5`")
    char_id_input = message.command[1]
    try:
        max_usage = int(message.command[2])
    except ValueError:
        return await message.reply_text("❌ Usage limit must be a number.")

    # 1. Verify character exists (Checking both String and Integer IDs)
    char = await characters.find_one({"id": {"$in": [str(char_id_input), char_id_input]}})
    
    if not char:
        return await message.reply_text(f"❌ No character found with ID: `{char_id_input}`")

    # 2. Generate unique 10-character code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # 3. Insert into gift_codes
    await gift_codes.insert_one({
        "code": code,
        "char_id": char['id'], # Link to the validated ID
        "max_usage": max_usage,
        "current_usage": 0,
        "users": [] 
    })

    await message.reply_text(
        f"✅ **Rᴇᴅᴇᴇᴍ Cᴏᴅᴇ Gᴇɴᴇʀᴀᴛᴇᴅ!**\n\n"
        f"🎁 **Cᴏᴅᴇ:** `{code}`\n"
        f"👤 **Wᴀɪғᴜ:** {char['name']}\n"
        f"👥 **Mᴀx Usᴇs:** {max_usage}\n\n"
        f"Players can now use: `/credeem {code}`"
    )