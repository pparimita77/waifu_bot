from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import groups
from sudo import OWNER_ID

# Define your full rarity list with emojis
RARITIES_MAP = {
    "Common": "⚪",
    "Rare": "🏵️",
    "Special": "🫧",
    "Legendary": "💮",
    "Limited": "🔮",
    "Celestial": "🎐",
    "Manga": "🔖",
    "Expensive": "💸",
    "Giveaway": "🧧",
    "Seasonal": "🍂",
    "Valentine": "💝",
    "AMV": "🎥"
}

async def get_allowed_rarities(chat_id):
    group_data = await groups.find_one({"_id": chat_id})
    if not group_data or "rarities" not in group_data:
        # Default: All rarities allowed if nothing is set
        return list(RARITIES_MAP.keys())
    return group_data["rarities"]

@Client.on_message(filters.command("rarity") & filters.group)
async def rarity_settings_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return # Strictly Bot Owner only

    allowed = await get_allowed_rarities(message.chat.id)
    
    text = (
        f"✨ **Rᴀʀɪᴛʏ Sᴘᴀᴡɴ Cᴏɴᴛʀᴏʟ**\n"
        f"Cʜᴀᴛ: `{message.chat.title}`\n\n"
        f"**Tap to toggle spawn availability:**"
    )

    buttons = []
    # Create buttons in rows of 2
    rarity_keys = list(RARITIES_MAP.keys())
    for i in range(0, len(rarity_keys), 2):
        row = []
        for r_name in rarity_keys[i:i+2]:
            emoji = RARITIES_MAP[r_name]
            status = "✅" if r_name in allowed else "❌"
            row.append(InlineKeyboardButton(
                f"{emoji} {r_name} {status}", 
                callback_data=f"tr_{r_name}_{message.chat.id}"
            ))
        buttons.append(row)
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^tr_"))
async def toggle_rarity_callback(client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("❌ Owner Only!", show_alert=True)

    data = query.data.split("_")
    r_name = data[1]
    chat_id = int(data[2])

    allowed = await get_allowed_rarities(chat_id)
    allowed = list(allowed)

    if r_name in allowed:
        allowed.remove(r_name)
    else:
        allowed.append(r_name)

    # Update Database
    await groups.update_one(
        {"_id": chat_id}, 
        {"$set": {"rarities": allowed}}, 
        upsert=True
    )

    # Rebuild buttons to show updated status
    buttons = []
    rarity_keys = list(RARITIES_MAP.keys())
    for i in range(0, len(rarity_keys), 2):
        row = []
        for name in rarity_keys[i:i+2]:
            emoji = RARITIES_MAP[name]
            status = "✅" if name in allowed else "❌"
            row.append(InlineKeyboardButton(
                f"{emoji} {name} {status}", 
                callback_data=f"tr_{name}_{chat_id}"
            ))
        buttons.append(row)

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await query.answer(f"{r_name} toggled!")