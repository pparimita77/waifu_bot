from pyrogram import Client, filters
from database import characters, claims
from sudo import is_dev  # Restricting to Owner and Devs

@Client.on_message(filters.command("delete") & is_dev)
async def delete_character(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🗑️ **Usᴀɢᴇ:** `/delete <char_id>`")

    char_id = message.command[1]

    # 1. Find the character first to show what was deleted
    char_to_delete = await characters.find_one({"id": char_id})
    
    if not char_to_delete:
        return await message.reply_text(f"❌ **Cʜᴀʀᴀᴄᴛᴇʀ Iᴅ `{char_id}` ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.**")

    char_name = char_to_delete.get("name", "Unknown")
    char_anime = char_to_delete.get("anime", "Unknown")

    # 2. Delete from characters collection
    await characters.delete_one({"id": char_id})

    # 3. Optional: Delete all instances of this character from user harems
    # Remove the next line if you want users to keep their deleted cards
    await claims.delete_many({"char_id": char_id})

    await message.reply_text(
        f"🗑️ **Cʜᴀʀᴀᴄᴛᴇʀ Dᴇʟᴇᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
        f"🌸 **Nᴀᴍᴇ:** {char_name}\n"
        f"🆔 **Iᴅ:** `{char_id}`\n"
        f"🍜 **Sᴏᴜʀᴄᴇ:** {char_anime}\n\n"
        f"⚠️ *Aʟʟ ᴇxɪsᴛɪɴɢ ᴄʟᴀɪᴍs ᴏғ ᴛʜɪs ᴄʜᴀʀᴀᴄᴛᴇʀ ʜᴀᴠᴇ ᴀʟsᴏ ʙᴇᴇɴ ᴘᴜʀɢᴇᴅ.*"
    )