import random
import string
from pyrogram import Client, filters
from config import OWNER_ID, DEVS
from database import db, characters

gift_codes = db.gift_codes

@Client.on_message(filters.command("gen_char") & filters.user([OWNER_ID] + DEVS))
async def generate_waifu_code(client, message):
    # Format: /gen_char <id> <usage>
    if len(message.command) < 3:
        return await message.reply_text("🌊 **Usᴀɢᴇ:** `/gen_char <char_id> <usage>`\nEx: `/gen_char 3546 5`")

    char_id = message.command[1]
    try:
        max_usage = int(message.command[2])
    except ValueError:
        return await message.reply_text("❌ Usᴀɢᴇ ᴍᴜsᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.")

    # Verify character exists
    char = await characters.find_one({"id": char_id})
    if not char:
        return await message.reply_text(f"❌ Nᴏ ᴄʜᴀʀᴀᴄᴛᴇʀ ғᴏᴜɴᴅ ᴡɪᴛʜ ID: `{char_id}`")

    # Generate 10-character code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    await gift_codes.insert_one({
        "code": code,
        "char_id": char_id,
        "max_usage": max_usage,
        "current_usage": 0,
        "users": [] # List of IDs who used it
    })

    await message.reply_text(
        f"✅ **Wᴀɪғᴜ Rᴇᴅᴇᴇᴍ Cᴏᴅᴇ Gᴇɴᴇʀᴀᴛᴇᴅ!**\n\n"
        f"🎁 **Cᴏᴅᴇ:** `{code}`\n"
        f"👤 **Wᴀɪғᴜ:** {char['name']}\n"
        f"👥 **Mᴀx Usᴇs:** {max_usage}\n\n"
        f"Pʟᴀʏᴇʀs ᴄᴀɴ ᴜsᴇ `/wredeem {code}`"
    )