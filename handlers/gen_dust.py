import random
import string
from pyrogram import Client, filters
from config import OWNER_ID, DEVS
from database import db

# Same authorized list
AUTHORIZED = [OWNER_ID] + DEVS + [12345678] 
dust_codes = db.dust_codes

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

@Client.on_message(filters.command("gen_dust") & filters.user(AUTHORIZED_USERS))
async def generate_dust_code(client, message):
    try:
        amount = int(message.command[1])
        limit = int(message.command[2])
    except (IndexError, ValueError):
        return await message.reply_text("✨ **Usᴀɢᴇ:** `/gen_dust <ᴀᴍᴏᴜɴᴛ> <ᴜsᴀɢᴇ_ʟɪᴍɪᴛ>`")

    code = "DUST-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    await dust_codes.insert_one({
        "code": code,
        "amount": amount,
        "limit": limit,
        "used_by": [] 
    })

    await message.reply_text(
        f"🌌 **Sᴛᴀʀᴅᴜsᴛ Cᴏᴅᴇ Gᴇɴᴇʀᴀᴛᴇᴅ!**\n\n"
        f"🎫 **Cᴏᴅᴇ:** `{code}`\n"
        f"💎 **Aᴍᴏᴜɴᴛ:** `{amount}` Sᴛᴀʀᴅᴜsᴛ\n"
        f"👥 **Mᴀx Usᴇs:** `{limit}`"
    )