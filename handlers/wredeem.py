from pyrogram import Client, filters
import datetime
from database import db, claims, characters

gift_codes = db.gift_codes

@Client.on_message(filters.command("wredeem"))
async def wredeem_waifu(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🌊 **Usᴀɢᴇ:** `/wredeem <CODE>`")

    user_id = message.from_user.id
    input_code = message.command[1].upper()

    # 1. Check if code exists
    gift = await gift_codes.find_one({"code": input_code})
    if not gift:
        return await message.reply_text("❌ Tʜɪs ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ.")

    # 2. Check if user already used THIS specific code
    if user_id in gift.get("users", []):
        return await message.reply_text("❌ Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ ᴛʜɪs ᴄᴏᴅᴇ!")

    # 3. Check usage limit
    if gift["current_usage"] >= gift["max_usage"]:
        return await message.reply_text("❌ Tʜɪs ᴄᴏᴅᴇ ʜᴀs ʀᴇᴀᴄʜᴇᴅ ɪᴛs ᴍᴀxɪᴍᴜᴍ ᴜsᴀɢᴇ.")

    # 4. Fetch Character details for the photo
    char = await characters.find_one({"id": gift["char_id"]})
    if not char:
        return await message.reply_text("❌ Character not found.")
    
    # 5. Add to user collection and update code status
    # MAKE SURE THESE LINES ARE ALIGNED WITH THE 'char =' ABOVE
    await claims.insert_one({
        "user_id": user_id,
        "char_id": char["id"],
        "date": datetime.datetime.now()
    })

    await gift_codes.update_one(
        {"code": input_code},
        {
            "$inc": {"current_usage": 1},
            "$push": {"users": user_id}
        }
    )

    # 6. Send success message with photo
    await message.reply_photo(
        photo=char['file_id'],
        caption=f"🎉 **Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!**\n\nYᴏᴜ ʀᴇᴅᴇᴇᴍᴇᴅ **{char['name']}** sᴜᴄᴄᴇssғᴜʟʟʏ!"
    )