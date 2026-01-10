import random
import string
from pyrogram import Client, filters
from database import db # Ensure 'db' is your motor database object

# Collection for the codes
dust_codes = db.dust_codes

@Client.on_message(filters.command("gen_dust"))
async def generate_dust_code(client, message):
    # Check if user is Admin (Optional but recommended)
    # if message.from_user.id not in ADMINS: return

    try:
        # Format: /gen_dust <amount> <usage_limit>
        amount = int(message.command[1])
        limit = int(message.command[2])
    except (IndexError, ValueError):
        return await message.reply_text("✨ **Usᴀɢᴇ:** `/gen_dust <ᴀᴍᴏᴜɴᴛ> <ᴜsᴀɢᴇ_ʟɪᴍɪᴛ>`\nEx: `/gen_dust 500 10`")

    # Generate a random 8-character code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    await dust_codes.insert_one({
        "code": code,
        "amount": amount,
        "limit": limit,
        "used_by": [] # Track user IDs who redeemed it
    })

    await message.reply_text(
        f"🌌 **Sᴛᴀʀᴅᴜsᴛ Cᴏᴅᴇ Gᴇɴᴇʀᴀᴛᴇᴅ!**\n\n"
        f"🎫 **Cᴏᴅᴇ:** `{code}`\n"
        f"💎 **Aᴍᴏᴜɴᴛ:** `{amount}` Sᴛᴀʀᴅᴜsᴛ\n"
        f"👥 **Mᴀx Usᴇs:** `{limit}`\n\n"
        f"Rᴇᴅᴇᴇᴍ Vɪᴀ: `/redeem {code}`"
    )