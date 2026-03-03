import datetime
from pyrogram import Client, filters
from database import users

# Replace with your actual ID
OWNER_ID = 123456789 

@Client.on_message(filters.command("add_subscription"))
async def add_sub(client, message):
    # 1. Permission Check
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ Oɴʟʏ ᴛʜᴇ Oᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    # 2. Argument Check
    args = message.command
    if len(args) < 3:
        return await message.reply_text("🎲 **Usage:** `/add_subscription <user_id> <days>`")

    try:
        target_id = int(args[1])
        days = int(args[2])
    except ValueError:
        return await message.reply_text("❌ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ User ID ᴀɴᴅ ɴᴜᴍʙᴇʀ ᴏғ ᴅᴀʏs.")

    # 3. Calculation & Database Update
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    
    # Using the same ID filter as your /bonus and /refer
    await users.update_one(
        {"$or": [{"user_id": target_id}, {"_id": target_id}]}, 
        {"$set": {
            "is_premium": True, 
            "sub_expiry": expiry
        }}, 
        upsert=True
    )

    await message.reply_text(
        f"✅ **Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Aᴅᴅᴇᴅ!**\n"
        f"👤 **Usᴇʀ ID:** `{target_id}`\n"
        f"⏳ **Dᴜʀᴀᴛɪᴏɴ:** `{days}` Dᴀʏs\n"
        f"📅 **Exᴘɪʀᴇs ᴏɴ:** `{expiry.strftime('%Y-%m-%d %H:%M')}`"
    )