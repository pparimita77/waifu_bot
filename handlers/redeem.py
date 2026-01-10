from pyrogram import Client, filters
from database import db, users

dust_codes = db.dust_codes

@Client.on_message(filters.command("redeem"))
async def redeem_code(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🎫 **Usᴀɢᴇ:** `/redeem <ᴄᴏᴅᴇ>`")

    input_code = message.command[1].upper()
    user_id = message.from_user.id

    # 1. Look for the code in dust_codes
    code_data = await dust_codes.find_one({"code": input_code})

    if not code_data:
        return await message.reply_text("❌ Iɴᴠᴀʟɪᴅ ᴏʀ Exᴘɪʀᴇᴅ Cᴏᴅᴇ.")

    # 2. Check if user already redeemed this specific code
    if user_id in code_data.get("used_by", []):
        return await message.reply_text("🚫 Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ ᴛʜɪs ᴄᴏᴅᴇ!")

    # 3. Check if usage limit is reached
    if len(code_data.get("used_by", [])) >= code_data["limit"]:
        return await message.reply_text("😔 Sᴏʀʀʏ! Tʜɪs ᴄᴏᴅᴇ ʜᴀs ʀᴇᴀᴄʜᴇᴅ ɪᴛs ᴍᴀxɪᴍᴜᴍ ᴜsᴀɢᴇ ʟɪᴍɪᴛ.")

    # 4. Successful Redemption
    amount = code_data["amount"]

    # Add Stardust to User Profile
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"stardust": amount}},
        upsert=True
    )

    # Add user to the 'used_by' list for this code
    await dust_codes.update_one(
        {"code": input_code},
        {"$push": {"used_by": user_id}}
    )

    await message.reply_text(
        f"🎉 **Rᴇᴅᴇᴇᴍ Sᴜᴄᴄᴇssғᴜʟ!**\n\n"
        f"🌌 Yᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ `{amount}` Sᴛᴀʀᴅᴜsᴛ.\n"
        f"💰 Cʜᴇᴄᴋ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ ᴡɪᴛʜ `/balance`."
    )