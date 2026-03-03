import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import users, claims, characters
from datetime import datetime

START_TEXT = """
🌊 Wᴇʟᴄᴏᴍᴇ Tᴏ Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ Gʀᴀʙʙᴇʀs Bᴏᴛ 

Lɪᴋᴇ Sᴛɪʟʟ Wᴀᴛᴇʀ Hɪᴅɪɴɢ Uɴᴍᴀᴛᴄʜᴇᴅ Sᴛʀᴇɴɢᴛʜ,
Tʜɪs Wᴏʀʟᴅ Is Fɪʟʟᴇᴅ Wɪᴛʜ Rᴀʀᴇ Sᴏᴜʟs Wᴀɪᴛɪɴɢ Tᴏ Bᴇ Fᴏᴜɴᴅ 💖
Sᴜᴍᴍᴏɴ Wᴀɪғᴜs, Cʟᴀɪᴍ Yᴏᴜʀ Fᴀᴠᴏʀɪᴛᴇs,
Aɴᴅ Bᴜɪʟᴅ A Cᴏʟʟᴇᴄᴛɪᴏɴ Wᴏʀᴛʜʏ Oғ A Tʀᴜᴇ Sʟᴀʏᴇʀ. ⚔️✨
Yᴏᴜʀ Jᴏᴜʀɴᴇʏ Bᴇɢɪɴs Nᴏᴡ💝

Aʀɪɢᴀᴛᴏ Gᴏᴢᴀɪᴍᴀsᴜ 💞
"""

@Client.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    
    # --- 1. REFERRAL LOGIC ---
    if len(message.command) > 1 and message.command[1].startswith("refer_"):
        try:
            referrer_id = int(message.command[1].replace("refer_", ""))
            
            check_user = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]})
            
            if not check_user and user_id != referrer_id:
                # Reward Referrer (200 Stardust + 10 Emeralds + Count)
                await users.update_one(
                    {"$or": [{"user_id": referrer_id}, {"_id": referrer_id}]},
                    {"$inc": {
                        "stardust": 200.0, 
                        "emeralds": 10, 
                        "referrals": 1
                    }},
                    upsert=True
                )

                # Reward New User (100 Stardust)
                await users.update_one(
                    {"user_id": user_id},
                    {"$inc": {"stardust": 100.0}},
                    upsert=True
                )
                
                # Notify Referrer
                try:
                    await client.send_message(
                        referrer_id, 
                        "🔔 **Nᴇᴡ Rᴇғᴇʀʀᴀʟ!**\n\nYᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ `200` Sᴛᴀʀᴅᴜsᴛ ᴀɴᴅ `10` Eᴍᴇʀᴀʟᴅs! 💎"
                    )
                except:
                    pass
        except Exception as e:
            print(f"Referral Error: {e}")

    # --- 2. MAIN START UI ---
    buttons = [
        [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="https://t.me/Tomioka_Supportcore"),
         InlineKeyboardButton("Uᴘᴅᴀᴛᴇ", url="https://t.me/Tomioka_Giyu_Updatecore")],
        [InlineKeyboardButton("Aᴅᴅ ᴍᴇ", url="https://t.me/Tomioka_Giyugrabbers_Bot?startgroup=true"),
         InlineKeyboardButton("Cʀᴇᴅɪᴛs", url="https://t.me/mnieuphoriasky")],
        [InlineKeyboardButton("💫 Rᴇғᴇʀ 💫", callback_data="refer_info")]
    ]
    
    await message.reply_text(START_TEXT, reply_markup=InlineKeyboardMarkup(buttons))

# --- 3. CALLBACK HANDLERS ---

@Client.on_callback_query(filters.regex("refer_info"))
async def refer_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_username = (await client.get_me()).username
    
    user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]})
    referrals = user_data.get("referrals", 0) if user_data else 0
    
    earned_stardust = referrals * 200
    earned_emeralds = referrals * 10
    refer_link = f"https://t.me/{bot_username}?start=refer_{user_id}"

    text = (
        "✅ **Rᴇғᴇʀʀᴀʟ Sʏsᴛᴇᴍ**\n\n"
        "🎁 Eᴀʀɴ **𝟸𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ** 🌟 & **𝟷𝟶 Eᴍᴇʀᴀʟᴅs** 💎 Fᴏʀ Eᴀᴄʜ Rᴇғᴇʀʀᴀʟ!\n\n"
        "📊 **Yᴏᴜʀ Sᴛᴀᴛs:**\n"
        f"   ╰─ 👥 Rᴇғᴇʀʀᴀʟs: `{referrals}`\n"
        f"   ╰─ 💰 Eᴀʀɴᴇᴅ: `{earned_stardust}` 🌟 | `{earned_emeralds}` 💎\n"
        f"   ╰─ 🔗 Yᴏᴜʀ Lɪɴᴋ:\n"
        f"      `{refer_link}`\n\n"
        "💡 **Hᴏᴡ Iᴛ Wᴏʀᴋs:**\n"
        "   • Sʜᴀʀᴇ Yᴏᴜʀ Rᴇғᴇʀʀᴀʟ Lɪɴᴋ\n"
        "   • Fʀɪᴇɴᴅ Jᴏɪɴs Usɪɴɢ Yᴏᴜʀ Lɪɴᴋ\n"
        "   • Yᴏᴜ Gᴇᴛ **𝟸𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ** 🌟 & **𝟷𝟶 Eᴍᴇʀᴀʟᴅs** 💎\n"
        "   • Yᴏᴜʀ Fʀɪᴇɴᴅ Rᴇᴄᴇɪᴠᴇs **𝟷𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ** 🌟\n\n"
        "🌟 Sᴛᴀʀᴛ Sʜᴀʀɪɴɢ Aɴᴅ Eᴀʀɴɪɴɢ!"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Sʜᴀʀᴇ Lɪɴᴋ", url=f"https://t.me/share/url?url={refer_link}&text=Join%20Tomioka%20Giyu%20Grabbers%20and%20get%20100%20Stardust!%20✨")],
        [InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="start_back")]
    ])

    await callback_query.message.edit_text(text, reply_markup=buttons)