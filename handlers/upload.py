from pyrogram import Client, filters
from config import OWNER_ID, DEVS, UPLOADERS
from database import characters

# Combine authorized users
AUTHORIZED = list(set([OWNER_ID] + DEVS + UPLOADERS))

@Client.on_message(filters.command("upload"))
async def upload_cmd(client, message):
    if not await check_staff(message.from_user.id, ["dev", "uploader"]):
        return await message.reply_text("❌ No permission.")
    # ... rest of code
    if not message.photo:
        return await message.reply_text("🌊 Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴛʜᴇ ᴄᴀᴘᴛɪᴏɴ.")

    # New Format: /upload Name | Anime | Rarity
    try:
        args = message.caption.split(" ", 1)[1].split("|")
        if len(args) != 3:
            raise IndexError

        name = args[0].strip()
        anime = args[1].strip()
        rarity = args[2].strip()
    except (IndexError, ValueError):
        return await message.reply_text(
            "❌ **Iɴᴠᴀʟɪᴅ Fᴏʀᴍᴀᴛ!**\n\n"
            "Usᴇ: `/upload Name | Anime | Rarity`\n"
            "Ex: `/upload Kakashi | Naruto | 2`"
        )

    # --- AUTO-INCREMENT LOGIC ---
    # Find the character with the highest ID
    last_char = await characters.find_one(sort=[("id", -1)])
    
    if last_char:
        # If ID is stored as string "1", convert to int, add 1, then back to string
        new_id = str(int(last_char['id']) + 1)
    else:
        # If database is empty, start at 1
        new_id = "1"
    # ----------------------------

    char_data = {
        "id": new_id,
        "name": name,
        "anime": anime,
        "rarity": rarity,
        "file_id": message.photo.file_id
    }

    await characters.insert_one(char_data)
    
    await message.reply_text(
        f"✅ **Cʜᴀʀᴀᴄᴛᴇʀ Uᴘʟᴏᴀᴅᴇᴅ!**\n\n"
        f"🆔 **Assɪɢɴᴇᴅ ID:** `{new_id}`\n"
        f"👤 **Nᴀᴍᴇ:** {name}\n"
        f"✨ **Rᴀʀɪᴛʏ:** {rarity}"
    )