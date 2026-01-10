from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscription_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚜️ Aᴄᴛɪᴠᴀᴛᴇ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ ⚜️", url="https://t.me/mnieuphoriasky")]
    ])

def get_refer_keyboard(ref_link):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💫 Rᴇғᴇʀ 💫", url=f"https://t.me/share/url?url={ref_link}")]
    ])