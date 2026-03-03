from pyrogram import Client, filters
from database import users
import config
from datetime import datetime

@Client.on_message(filters.command("check_sub") & filters.user(config.OWNER_ID))
async def check_subscription(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>⚠️ Usᴀɢᴇ:</b> <code>/check_sub [user_id]</code>")

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("<b>❌ Eʀʀᴏʀ:</b> Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ a ᴠᴀʟɪᴅ User ID.")

    # Fetch User Data
    user_data = await users.find_one({"_id": target_id})
    
    if not user_data:
        return await message.reply_text("<b>🔍 Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.</b>")

    is_premium = user_data.get("is_premium", False)
    expiry = user_data.get("premium_expiry")

    if not is_premium or not expiry:
        return await message.reply_text(f"👤 <b>Usᴇʀ:</b> <code>{target_id}</code>\n❌ <b>Sᴛᴀᴛᴜs:</b> Nᴏᴛ a Pʀᴇᴍɪᴜᴍ Usᴇʀ.")

    # Calculate Time Remaining
    now = datetime.now()
    if expiry > now:
        time_left = expiry - now
        days = time_left.days
        hours = time_left.seconds // 3600
        
        status_text = (
            f"👤 <b>Usᴇʀ:</b> <code>{target_id}</code>\n"
            f"✅ <b>Sᴛᴀᴛᴜs:</b> Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴇ\n"
            f"📅 <b>Exᴘɪʀʏ:</b> <code>{expiry.strftime('%Y-%m-%d %H:%M')}</code>\n"
            f"⏳ <b>Rᴇᴍᴀɪɴɪɴɢ:</b> <code>{days}ᴅ {hours}ʜ</code>"
        )
    else:
        status_text = (
            f"👤 <b>Usᴇʀ:</b> <code>{target_id}</code>\n"
            f"❌ <b>Sᴛᴀᴛᴜs:</b> Pʀᴇᴍɪᴜᴍ Exᴘɪʀᴇᴅ\n"
            f"📅 <b>Exᴘɪʀᴇᴅ ᴏɴ:</b> <code>{expiry.strftime('%Y-%m-%d')}</code>"
        )

    await message.reply_text(status_text)