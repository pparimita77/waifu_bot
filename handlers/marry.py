import random
from pyrogram import Client, filters
from database import users, characters

@Client.on_message(filters.command("marry"))
async def marry_waifu(_, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("Pʟᴇᴀsᴇ Pʀᴏᴠɪᴅᴇ A Cʜᴀʀᴀᴄᴛᴇʀ Iᴅ!")

    char_id = message.command[1]
    user = await users.find_one({"_id": user_id})

    # Check if user actually owns the waifu
    if not user or char_id not in user.get("harem", []):
        return await message.reply("Sʜᴇ's Nᴏᴛ Iɴ Yᴏᴜʀ Lᴜᴄᴋ 🤞")

    char = await characters.find_one({"id": char_id})
    
    # Marriage Success Logic (e.g., 30% chance)
    success = random.randint(1, 100) <= 30

    if success:
        text = (
            "🌊 Wɪᴛʜ A Qᴜɪᴇᴛ Pʀᴏᴍɪsᴇ, Yᴏᴜ Sᴛᴇᴘ Fᴏʀᴡᴀʀᴅ.💖\n"
            "Sʜᴇ Aᴄᴄᴇᴘᴛs Yᴏᴜʀ Hᴀɴᴅ Wɪᴛʜᴏᴜᴛ Hᴇsɪᴛᴀᴛɪᴏɴ🌷\n\n"
            f"🆔 ɪᴅ: {char['id']}\n"
            f"🌊 ɴᴀᴍᴇ: {char['name']}\n"
            f"💫 ʀᴀʀɪᴛʏ: {char['rarity']}\n"
            f"🥢 sᴏᴜʀᴄᴇ: {char['anime']}"
        )
        # Add to 'married' list in DB
        await users.update_one({"_id": user_id}, {"$push": {"married": char_id}})
    else:
        text = "Sʜᴇ's Nᴏᴛ Iɴ Yᴏᴜʀ Lᴜᴄᴋ 🤞 (Sʜᴇ Rᴇᴊᴇᴄᴛᴇᴅ Yᴏᴜ)"

    await message.reply_text(text)