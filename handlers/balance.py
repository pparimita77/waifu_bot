from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ParseMode
from database import users

# --- CONFIGURATION ---
AUTH_CHANNEL = "@Tomioka_Supportcore"

async def is_subscribed(client, user_id):
    try:
        await client.get_chat_member(AUTH_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True

@Client.on_message(filters.command(["balance", "bal"]))
async def balance(client, message):
    try:
        user_id = message.from_user.id
        
        # --- FORCE JOIN CHECK ---
        if not await is_subscribed(client, user_id):
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Jᴏɪɴ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ", url=f"https://t.me/{AUTH_CHANNEL}")],
                [InlineKeyboardButton("🔄 Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{client.me.username}?start=check")]
            ])
            return await message.reply_text(
                "❌ <b>Aᴄᴄᴇss Dᴇɴɪᴇᴅ!</b>\n\nYᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ.",
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )

        # 1. Broad Search: Check all possible ID keys
        user_data = await users.find_one({
            "$or": [
                {"user_id": user_id}, 
                {"_id": user_id}, 
                {"id": user_id}
            ]
        })
        
        # 2. Database Auto-Repair Logic
        # If user exists but fields are missing, or user is totally new
        if not user_data:
            stardust = 0.0
            emeralds = 0.0
            # Create the user if they don't exist to prevent future 0 bal issues
            await users.update_one(
                {"user_id": user_id},
                {"$setOnInsert": {"stardust": 0.0, "emeralds": 0.0, "username": message.from_user.username}},
                upsert=True
            )
        else:
            # Safely extract values, fallback to 0.0 if key is missing or corrupted
            def safe_float(value):
                try:
                    return float(value) if value is not None else 0.0
                except (ValueError, TypeError):
                    return 0.0

            stardust = safe_float(user_data.get('stardust'))
            emeralds = safe_float(user_data.get('emeralds'))

        # 3. Final Formatting
        text = (
            f"⛩️ <b>Kᴏɴɴɪᴄʜɪᴡᴀ {message.from_user.first_name}-Sᴀɴ!</b> 💫\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏦 <b>Yᴏᴜʀ Cᴜʀʀᴇɴᴛ Bᴀʟᴀɴᴄᴇ</b>\n\n"
            f"🌟 <b>Sᴛᴀʀᴅᴜsᴛ:</b> <code>{stardust:,.2f}</code>\n"
            f"💠 <b>Eᴍᴇʀᴀʟᴅs:</b> <code>{emeralds:,.2f}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        
        await message.reply_text(text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        print(f"Error in balance command: {e}")