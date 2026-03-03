from pyrogram import Client, filters
from datetime import datetime
from database import db, claims, characters

gift_codes = db.gift_codes

# Added group=0 to ensure it beats the spawn counter
@Client.on_message(filters.command("wredeem") & filters.group, group=0)
async def wredeem_waifu(client, message):
    if not message.from_user:
        return

    if len(message.command) < 2:
        return await message.reply_text("🌊 **Usᴀɢᴇ:** `/wredeem <CODE>`")

    user_id = message.from_user.id
    input_code = message.command[1].upper()

    # 1. Fetch the gift data
    gift = await gift_codes.find_one({"code": input_code})
    if not gift:
        return await message.reply_text("❌ Tʜɪs ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ.")

    # 2. Check usage limit
    current = gift.get("current_usage", 0)
    maximum = gift.get("max_usage", 0)
    if current >= maximum:
        return await message.reply_text("❌ Tʜɪs ᴄᴏᴅᴇ ʜᴀs ʀᴇᴀᴄʜᴇᴅ ɪᴛs ᴍᴀxɪᴍᴜᴍ ᴜsᴀɢᴇ.")

    # 3. Check if user already used it
    if user_id in gift.get("users", []):
        return await message.reply_text("❌ Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ ᴛʜɪs ᴄᴏᴅᴇ!")

    # 4. Universal Character Fetch (tries string and int)
    char_id = gift.get("char_id")
    char = await characters.find_one({"id": {"$in": [str(char_id), char_id]}})
    
    if not char:
        return await message.reply_text("❌ Error: The character in this code no longer exists.")
    
    # 5. Atomic Update and Insert
    try:
        # Add to Harem
        await claims.insert_one({
            "user_id": user_id,
            "char_id": char["id"],
            "date": datetime.now()
        })

        # Update Code Usage
        await gift_codes.update_one(
            {"code": input_code},
            {
                "$inc": {"current_usage": 1},
                "$push": {"users": user_id}
            }
        )

        # 6. Success Response
        await message.reply_photo(
            photo=char['file_id'],
            caption=(
                f"🎉 **Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!**\n\n"
                f"👤 **Usᴇʀ:** {message.from_user.mention}\n"
                f"✅ Yᴏᴜ ʀᴇᴅᴇᴇᴍᴇᴅ **{char['name']}** sᴜᴄᴄᴇssғᴜʟʟʏ!\n"
                f"📺 **Aɴɪᴍᴇ:** {char['anime']}"
            )
        )
    except Exception as e:
        print(f"Redeem Error: {e}")
        await message.reply_text("❌ A database error occurred. Try again later.")