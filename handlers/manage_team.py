from pyrogram import Client, filters
from config import OWNER_ID
from database import db

# This line is OUTSIDE the fumnction, so it has NO spaces
staff_db = db.staff 

@Client.on_message(filters.command("add_dev") & filters.user(OWNER_ID))
async def add_developer(client, message):
    # These lines are INSIDE the function, so they MUST have 4 spaces
    if len(message.command) < 2:
        return await message.reply_text("🌊 Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ Usᴇʀ ID.")
    
    user_id = int(message.command[1])
    await staff_db.update_one({"_id": "devs"}, {"$addToSet": {"ids": user_id}}, upsert=True)
    await message.reply_text(f"✅ Usᴇʀ {user_id} ᴀᴅᴅᴇᴅ ᴛᴏ Dᴇᴠᴇʟᴏᴘᴇʀs.")