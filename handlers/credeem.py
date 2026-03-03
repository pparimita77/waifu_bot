from pyrogram import Client, filters
from database import db, characters  
from datetime import datetime

# Accessing the collections
gift_codes = db.gift_codes
user_collection = db.users
claims = db.claims 

@Client.on_message(filters.command("credeem"))
async def redeem_character(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/credeem <CODE>`")

    redeem_code = message.command[1].upper()
    user_id = message.from_user.id

    # 1. Verify if the code exists
    gift = await gift_codes.find_one({"code": redeem_code})

    if not gift:
        return await message.reply_text("❌ **Invalid Code:** This code does not exist or has expired.")

    # 2. Check usage limit
    if gift['current_usage'] >= gift['max_usage']:
        return await message.reply_text("🚫 **Limit Reached:** This code has already been fully used.")

    # 3. Prevent double claims
    if user_id in gift.get('users', []):
        return await message.reply_text("☝️ **Already Claimed:** You have already used this code once.")

    # 4. Fetch the character info
    char = await characters.find_one({"id": gift['char_id']})
    if not char:
        return await message.reply_text("❌ **Error:** The character linked to this code no longer exists.")

    # 5. DATABASE UPDATES
    await gift_codes.update_one(
        {"code": redeem_code},
        {
            "$inc": {"current_usage": 1},
            "$push": {"users": user_id}
        }
    )

    await claims.insert_one({
        "user_id": user_id,
        "char_id": char['id'],
        "name": char['name'],
        "anime": char['anime'],
        "rarity": char['rarity'],
        "date": datetime.now() 
    })

    await user_collection.update_one(
        {"user_id": user_id},
        {"$push": {"collection": char['id']}},
        upsert=True
    )

    # 6. Success Response Logic
    caption = (
        f"🎉 **Sᴜᴄᴄᴇssғᴜʟʟʏ Rᴇᴅᴇᴇᴍᴇᴅ!**\n\n"
        f"👤 **Nᴀᴍᴇ:** {char['name']}\n"
        f"🎌 **Aɴɪᴍᴇ:** {char['anime']}\n"
        f"🆔 **ID:** `{char['id']}`\n"
        f"✨ **Rᴀʀɪᴛʏ:** {char['rarity']}\n\n"
        f"🌸 _This character has been added to your /harem!_"
    )

    file_id = char['file_id']
    is_video = char.get("is_video", False) # Check the flag from cupload

    try:
        if is_video:
            # Send as video if it's an AMV
            await message.reply_video(video=file_id, caption=caption)
        else:
            # Send as photo for regular rarities
            await message.reply_photo(photo=file_id, caption=caption)
    except Exception:
        # Fallback to text if file_id is invalid or missing
        await message.reply_text(caption)