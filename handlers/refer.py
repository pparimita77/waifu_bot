from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users

@Client.on_message(filters.command("refer"))
async def refer_system(client, message):
    user_id = message.from_user.id
    user = await users.find_one({"_id": user_id}) or {}
    
    ref_count = user.get("referrals", 0)
    earned = ref_count * 300
    bot_username = (await client.get_me()).username
    ref_link = f"https://t.me/Tomioka_Giyugrabbers_Bot?start=ref_{user_id}"

    text = (
        "👥 Rᴇғᴇʀʀᴀʟ Sʏsᴛᴇᴍ\n\n"
        "🎁 Eᴀʀɴ 𝟹𝟶𝟶 Gᴇᴍs 💎 & 𝟸𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ Fᴏʀ Eᴀᴄʜ Rᴇғᴇʀʀᴀʟ!\n\n"
        "📊 Yᴏᴜʀ Sᴛᴀᴛs:\n"
        f"   ╰─ 👥 Rᴇғᴇʀʀᴀʟs: {ref_count}\n"
        f"   ╰─ 💰 Eᴀʀɴᴇᴅ: {earned} Gems\n"
        f"   ╰─ 🔗 Yᴏᴜʀ Lɪɴᴋ:\n"
        f"      `{ref_link}`\n\n"
        "💡 Hᴏᴡ Iᴛ Wᴏʀᴋs:\n"
        "   • Sʜᴀʀᴇ Yᴏᴜʀ Rᴇғᴇʀʀᴀʟ Lɪɴᴋ\n"
        "   • Fʀɪᴇɴᴅ Jᴏɪɴs Usɪɴɢ Yᴏᴜʀ Lɪɴᴋ\n"
        "   • Yᴏᴜ Gᴇᴛ 𝟹𝟶𝟶 Gᴇᴍs 💎 & 𝟸𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ\n"
        "   • Yᴏᴜʀ Fʀɪᴇɴᴅ Gᴇᴛs 𝟸𝟶𝟶 Gᴇᴍs 💎 & 𝟷𝟶𝟶 Sᴛᴀʀᴅᴜsᴛ\n"
        "   • Gᴇᴛ Aɴ Aᴍᴀᴢɪɴɢ Pʀɪᴢᴇ Aғᴛᴇʀ 𝟻 Rᴇғᴇʀʀᴀʟs!"
    )

    buttons = [[InlineKeyboardButton("💫 Rᴇғᴇʀ 💫", url=f"https://t.me/share/url?url={ref_link}")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))