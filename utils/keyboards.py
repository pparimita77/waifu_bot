from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_buttons(bot_username):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me", url=f"https://t.me/Tomioka_Giyugrabbers_Bot?startgroup=true")
        ],
        [
            InlineKeyboardButton("🔔 Updates", url="https://t.me/Tomioka_Giyu_Updatecore"),
            InlineKeyboardButton("🆘 Support", url="https://t.me/Tomioka_Supportcore")
        ],
        [
            InlineKeyboardButton("👑 Owner", url="https://t.me/mnieuphoriasky"),
            InlineKeyboardButton("⚙️ Developer", url="https://t.me/DemonKamadoTanjiro")
        ]
    ])

def mode_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚪", callback_data="mode_1"),
            InlineKeyboardButton("💮", callback_data="mode_2"),
            InlineKeyboardButton("🏵️", callback_data="mode_3")
        ],
        [
            InlineKeyboardButton("🫧", callback_data="mode_4"),
            InlineKeyboardButton("🔮", callback_data="mode_5"),
            InlineKeyboardButton("🎐", callback_data="mode_6")
        ],
        [
            InlineKeyboardButton("💸", callback_data="mode_7"),
            InlineKeyboardButton("🧧", callback_data="mode_8"),
            InlineKeyboardButton("🍂", callback_data="mode_9")
        ],
        [
            InlineKeyboardButton("💝", callback_data="mode_10"),
            InlineKeyboardButton("🔖", callback_data="mode_11"),
            InlineKeyboardButton("🎥", callback_data="mode_12")
        ]
    ])
