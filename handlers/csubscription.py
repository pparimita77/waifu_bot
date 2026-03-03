from pyrogram import Client, filters, types
import config
from database import users, set_premium
from datetime import datetime
import traceback

# --- 1. /subscription Command (With Group Priority) ---
@Client.on_message(filters.command("subscription") & filters.group)
async def subscription_info(client, message):
    print(f"DEBUG: Subscription command triggered by {message.from_user.id}")
    
    user_id = message.from_user.id
    
    try:
        # Check for both '_id' and 'user_id' to be safe
        user_data = await users.find_one({"_id": user_id}) or await users.find_one({"user_id": user_id}) or {}
        
        is_premium = user_data.get("is_premium", False)
        expiry = user_data.get("premium_expiry")
        
        status_text = "❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ a Pʀᴇᴍɪᴜᴍ Usᴇʀ."
        if is_premium and expiry:
            # Handle both datetime objects and strings from DB
            if isinstance(expiry, str):
                try:
                    expiry = datetime.strptime(expiry, '%Y-%m-%d')
                except:
                    expiry = None

            if expiry and expiry > datetime.now():
                status_text = f"✅ Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴇ ᴜɴᴛɪʟ: {expiry.strftime('%Y-%m-%d')}"
            else:
                status_text = "❌ Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ ʜᴀs ᴇxᴘɪʀᴇᴅ."

        text = (
            "🏆 <b>Pʀᴇᴍɪᴜᴍ Pᴀss Bᴇɴᴇғɪᴛs</b> 🏆\n\n"
            "🔥 <b>Exᴄʟᴜsɪᴠᴇ Aᴅᴠᴀɴᴛᴀɢᴇs:</b>\n\n"
            "🎰 <b>/sʟᴏᴛ → Hɪɢʜᴇʀ Rᴇᴡᴀʀᴅs!</b>\n"
            "   • Nᴏʀᴍᴀʟ: 𝟷𝟶-𝟹𝟶 Sᴛᴀʀᴅᴜsᴛ\n"
            "   • Pʀᴇᴍɪᴜᴍ: Uᴘ Tᴏ 𝟷𝟶𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ!\n\n"
            "🎁 <b>/ᴄʟᴀɪᴍ → Dᴀɪʟʏ Tʀɪᴘʟᴇ Cʟᴀɪᴍs!</b>\n"
            "   • Nᴏʀᴍᴀʟ: 𝟷 Cʟᴀɪᴍ/Dᴀʏ\n"
            "   • Pʀᴇᴍɪᴜᴍ: 𝟹 Cʟᴀɪᴍs/Dᴀʏ\n\n"
            "💎 <b>Exᴛʀᴀ Pᴇʀᴋs:</b>\n"
            "   • Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs Oɴ Pʀᴏғɪʟᴇ\n"
            "   • Pʀɪᴏʀɪᴛʏ Iɴ Eᴠᴇɴᴛs\n\n"
            "💰 <b>Pʀɪᴄɪɴɢ:</b>\n"
            "   • 𝟷 Wᴇᴇᴋ → ₹𝟷𝟿\n"
            "   • 𝟷 Mᴏɴᴛʜ → ₹𝟺𝟿\n\n"
            f"📢 <b>Yᴏᴜʀ Sᴛᴀᴛᴜs:</b> {status_text}\n\n"
            "Rᴇᴀᴅʏ Tᴏ Dᴏᴍɪɴᴀᴛᴇ? Aᴄᴛɪᴠᴀᴛᴇ Pʀᴇᴍɪᴜᴍ Nᴏᴡ!"
        )
        
        buttons = [[types.InlineKeyboardButton("⚜️ Aᴄᴛɪᴠᴀᴛᴇ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ ⚜️", url="https://t.me/mnieuphoriasky")]]
        await message.reply_text(text, reply_markup=types.InlineKeyboardMarkup(buttons))

    except Exception as e:
        print(f"SUBSCRIPTION ERROR: {traceback.format_exc()}")

# --- 2. /add_subscription Command (OWNER ONLY) ---
@Client.on_message(filters.command("add_subscription") & filters.user(config.OWNER_ID), group=-1)
async def add_sub(client, message):
    if len(message.command) < 3:
        return await message.reply_text("<b>Usᴀɢᴇ:</b> <code>/add_subscription [user_id] [days]</code>")
    
    try:
        target_id = int(message.command[1])
        days = int(message.command[2])
        
        expiry = await set_premium(target_id, days)
        
        await message.reply_text(
            f"✅ <b>Pʀᴇᴍɪᴜᴍ Aᴅᴅᴇᴅ!</b>\n"
            f"👤 <b>Usᴇʀ ID:</b> <code>{target_id}</code>\n"
            f"⏳ <b>Dᴜʀᴀᴛɪᴏɴ:</b> {days} Dᴀʏs\n"
            f"📅 <b>Exᴘɪʀᴇs:</b> {expiry.strftime('%Y-%m-%d') if expiry else 'Error'}"
        )
        
        try:
            await client.send_message(target_id, "🎉 <b>Cᴏɴɢʀᴀᴛs! Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\nUsᴇ /subscription ᴛᴏ ᴄʜᴇᴄᴋ ᴅᴇᴛᴀɪʟs.")
        except:
            pass
            
    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")