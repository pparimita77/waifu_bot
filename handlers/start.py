from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
async def start(_, message):
    buttons = [
        [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="https://t.me/Tomioka_Supportcore"),
         InlineKeyboardButton("Uᴘᴅᴀᴛᴇ", url="https://t.me/Tomioka_Giyu_Updatecore")],
        [InlineKeyboardButton("Aᴅᴅ ᴍᴇ", url="https://t.me/Tomioka_Giyugrabbers_Bot?startgroup=true"),
         InlineKeyboardButton("Cʀᴇᴅɪᴛs", url="https://t.me/mnieuphoriasky")],
        [InlineKeyboardButton("Rᴇғᴇʀ", callback_data="refer_info")]
    ]
    await message.reply_text(START_TEXT, reply_markup=InlineKeyboardMarkup(buttons))