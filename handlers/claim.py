from pyrogram import Client, filters
from database import users, characters, claims # Added 'claims'
import datetime

@Client.on_message(filters.command("claim"))
async def claim_waifu(_, message):
    user_id = message.from_user.id
    # Fetch user data or set defaults
    user = await users.find_one({"_id": user_id}) or {"claims": 0, "is_premium": False, "last_claim": ""}
    
    limit = 3 if user.get("is_premium") else 1
    today = str(datetime.date.today())

    # Check if user reached their daily limit
    if user.get("last_claim") == today and user.get("claims", 0) >= limit:
        return await message.reply_text(
            "Yᴏᴜ Rᴇᴀᴄʜᴇᴅ Yᴏᴜʀ Dᴀɪʟʏ Lɪᴍɪᴛs 🙏\n\n"
            "Aᴄᴛɪᴠᴀᴛᴇ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Fᴏʀ Mᴏʀᴇ Rᴇᴡᴀʀᴅs ✨"
        )

    # Pick random character logic
    char_list = await characters.aggregate([{"$sample": {"size": 1}}]).to_list(1)
    if not char_list: 
        return await message.reply_text("Nᴏ Wᴀɪғᴜs Aᴠᴀɪʟᴀʙʟᴇ Iɴ Dᴀᴛᴀʙᴀsᴇ!")
    
    char = char_list[0]

    # 1. Update user's claim counter
    await users.update_one(
        {"_id": user_id}, 
        {"$inc": {"claims": 1}, "$set": {"last_claim": today}}, 
        upsert=True
    )

    # 2. Add character to the user's harem (claims collection)
    await claims.insert_one({
        "user_id": user_id,
        "char_id": char['id'],
        "date": datetime.datetime.now()
    })
    
    # 3. Send success message (Fixed multiline formatting)
    await message.reply_text(
        f"🌊 Tʜɪs Wᴀɪғᴜ Nᴏᴡ Bᴇʟᴏɴɢs Tᴏ Yᴏᴜ {message.from_user.first_name}-Cʜᴀɴ 💙\n\n"
        f"🌸 **Iᴅ:** `{char['id']}`\n"
        f"💫 **Nᴀᴍᴇ:** {char['name']}\n"
        f"🌈 **Rᴀʀɪᴛʏ:** {char['rarity']}\n"
        f"🍜 **Sᴏᴜʀᴄᴇ:** {char['anime']}"
    )