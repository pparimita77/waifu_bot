from pyrogram import Client, filters
from database import users
import datetime

@Client.on_message(filters.command("add_subscription"))
async def add_sub(_, message):
    # Only Owner can use this
    args = message.command
    target_id = int(args[1])
    days = int(args[2])
    
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    await users.update_one(
        {"_id": target_id}, 
        {"$set": {"is_premium": True, "sub_expiry": expiry}}, 
        upsert=True
    )
    await message.reply(f"✅ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Aᴅᴅᴇᴅ Fᴏʀ {days} Dᴀʏs.")