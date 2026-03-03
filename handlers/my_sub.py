import html
from datetime import datetime
from pyrogram import Client, filters
from database import users 

@Client.on_message(filters.command("my_sub"))
async def my_subscription(client, message):
    user_id = message.from_user.id
    user_name = html.escape(message.from_user.first_name)
    
    # Universal check for user data
    user_data = await users.find_one({"$or": [{"_id": user_id}, {"user_id": user_id}]})
    
    # 1. Check if user exists or has premium
    if not user_data or not user_data.get("is_premium"):
        return await message.reply_text(
            "❌ <b>Yᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.</b>\n\n"
            "🌟 ᴛʏᴘᴇ /subscription ᴛᴏ ᴠɪᴇᴡ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs ᴀɴᴅ ʙᴇɴᴇғɪᴛs!"
        )

    expiry = user_data.get("premium_expiry")
    now = datetime.now()

    # 2. Safety check for expiry type and date
    if not expiry or not isinstance(expiry, datetime) or expiry < now:
        # Auto-reset if expired but flag still True
        await users.update_one(
            {"$or": [{"_id": user_id}, {"user_id": user_id}]},
            {"$set": {"is_premium": False}}
        )
        return await message.reply_text(
            "❌ <b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ᴇxᴘɪʀᴇᴅ.</b>\n"
            "ᴘʟᴇᴀsᴇ ʀᴇɴᴇᴡ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴇɴᴊᴏʏɪɴɢ ᴘᴇʀᴋs!"
        )

    # 3. Calculate time remaining
    time_left = expiry - now
    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds // 60) % 60

    # 4. Build the response with Perk Summary
    text = (
        f"👑 <b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs</b> 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Usᴇʀ:</b> {user_name}\n"
        f"📅 <b>Exᴘɪʀᴇs Oɴ:</b> <code>{expiry.strftime('%d %b %Y')}</code>\n"
        f"⏳ <b>Rᴇᴍᴀɪɴɪɴɢ:</b> <code>{days}ᴅ {hours}ʜ {minutes}ᴍ</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Aᴄᴛɪᴠᴇ Pᴇʀᴋs:</b>\n"
        f"🎁 <b>Cʟᴀɪᴍs:</b> <code>𝟹 ᴘᴇʀ ᴅᴀʏ</code> (ᴛʀɪᴘʟᴇ!)\n"
        f"🎰 <b>Sʟᴏᴛs:</b> <code>𝟹𝟶-𝟻𝟶 Eᴍᴇʀᴀʟᴅs</code> + <code>Sᴛᴀʀᴅᴜsᴛ</code>\n"
        f"🏆 <b>Pʀᴏғɪʟᴇ:</b> <code>Pʀᴇᴍɪᴜᴍ Bᴀᴅɢᴇ ᴀᴄᴛɪᴠᴇ</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ <i>Tʜᴀɴᴋ ʏᴏᴜ ғᴏʀ sᴜᴘᴘᴏʀᴛɪɴɢ Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ!</i>"
    )

    await message.reply_text(text)