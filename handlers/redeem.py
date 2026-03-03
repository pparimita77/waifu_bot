from pyrogram import Client, filters
from database import db, users

dust_codes = db.dust_codes

@Client.on_message(filters.command("redeem"))
async def redeem_code(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🎫 **Usᴀɢᴇ:** `/redeem <ᴄᴏᴅᴇ>`")

    input_code = message.command[1].upper()
    user_id = message.from_user.id

    # 1. Look for the code
    code_data = await dust_codes.find_one({"code": input_code})

    if not code_data:
        return await message.reply_text("❌ Iɴᴠᴀʟɪᴅ ᴏʀ Exᴘɪʀᴇᴅ Cᴏᴅᴇ.")

    # 2. Check usage list
    used_by = code_data.get("used_by", [])
    if user_id in used_by:
        return await message.reply_text("🚫 Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ ᴛʜɪs ᴄᴏᴅᴇ!")

    # 3. Check usage limit
    if len(used_by) >= code_data.get("limit", 0):
        return await message.reply_text("😔 Sᴏʀʀʏ! Tʜɪs ᴄᴏᴅᴇ ʜᴀs ʀᴇᴀᴄʜᴇᴅ ɪᴛs ʟɪᴍɪᴛ.")

    # 4. Successful Redemption
    amount = float(code_data["amount"]) # Ensure it is a float for Stardust

    # FIX: Use the same filter as your /balance command to find the user
    user_filter = {"$or": [{"user_id": user_id}, {"_id": user_id}]}
    
    # Update Stardust balance
    await users.update_one(
        user_filter,
        {"$inc": {"stardust": amount}},
        upsert=True
    )

    # Add user to the 'used_by' list for this code
    await dust_codes.update_one(
        {"code": input_code},
        {"$push": {"used_by": user_id}}
    )

    await message.reply_text(
        f"🎉 **Rᴇᴅᴇᴇᴍ Sᴜᴄᴄᴇssғᴜʟ!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌌 **Rᴇᴄᴇɪᴠᴇᴅ:** 🌟 `{amount:,.2f}` Sᴛᴀʀᴅᴜsᴛ\n"
        f"💰 Cʜᴇᴄᴋ ʏᴏᴜʀ `/balance` ɴᴏᴡ!\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )