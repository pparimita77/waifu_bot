from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users

@Client.on_message(filters.command("refer") & filters.group, group=0)
async def refer_command(client, message):
    user_id = message.from_user.id
    
    # Fetch user data
    user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]})
    if not user_data:
        user_data = {}

    referrals = user_data.get("referrals", 0)
    earned_stardust = referrals * 200
    earned_emeralds = referrals * 10
    refer_link = f"https://t.me/Tomioka_Giyugrabbers_Bot?start=refer_{user_id}"

    text = (
        "👥 **Rᴇғᴇʀʀᴀʟ Sʏsᴛᴇᴍ**\n\n"
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
        "   • Yᴏᴜʀ Fʀɪᴇɴᴅ Wɪʟʟ Rᴇᴄᴇɪᴠᴇ **𝟷𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ** 🌟\n"
        "   • Uɴʟɪᴍɪᴛᴇᴅ Rᴇғᴇʀʀᴀʟs!\n\n"
        "🌟 Sᴛᴀʀᴛ Sʜᴀʀɪɴɢ Aɴᴅ Eᴀʀɴɪɴɢ!"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🚀 Sʜᴀʀᴇ Lɪɴᴋ", 
                url=f"https://t.me/share/url?url={refer_link}&text=Join%20this%20amazing%20bot%20and%20get%20100%20Stardust%20instantly!%20✨"
            )
        ],
        [
            InlineKeyboardButton("📜 Mʏ Rᴇғᴇʀʀᴀʟ Lɪsᴛ", callback_data="view_referrals")
        ]
    ])

    await message.reply_text(text, reply_markup=buttons)