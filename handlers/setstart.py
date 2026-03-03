from pyrogram import Client, filters
from config import DEVS  # Import your dev list

@Client.on_message(filters.command("setstart") & filters.user("DEVS"))
async def set_start_msg(_, message):
    if not message.reply_to_message:
        return await message.reply("Rᴇᴘʟʏ Tᴏ A Mᴇssᴀɢᴇ Tᴏ Sᴇᴛ Iᴛ As Sᴛᴀʀᴛ Tᴇxᴛ.")
    
    new_start = message.reply_to_message.text
    await db.settings.update_one({"_id": "start_config"}, {"$set": {"text": new_start}}, upsert=True)
    await message.reply("✅ Sᴛᴀʀᴛ Mᴇssᴀɢᴇ Uᴘᴅᴀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ.")