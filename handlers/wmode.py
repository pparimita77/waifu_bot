from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import users

# Complete Rarity List
RARITIES = {
    "Common": "⚪", "Rare": "🏵️", "Special": "🫧", "Legendary": "💮",
    "Limited": "🔮", "Celestial": "🎐", "Manga": "🔖", "Expensive": "💸",
    "Giveaway": "🧧", "Seasonal": "🍂", "Valentine": "💝", "AMV": "🎥"
}

@Client.on_message(filters.command("wmode"))
async def wmode_command(client, message):
    user_id = message.from_user.id
    
    buttons = []
    rarity_keys = list(RARITIES.keys())

    # Create 2-column grid
    for i in range(0, len(rarity_keys), 2):
        row = [
            InlineKeyboardButton(f"{RARITIES[r]} {r}", callback_data=f"wmset_{r}") 
            for r in rarity_keys[i:i+2]
        ]
        buttons.append(row)

    buttons.append([InlineKeyboardButton("✨ Sʜᴏᴡ Aʟʟ", callback_data="wmset_all")])

    await message.reply_text(
        "✨ **Hᴀʀᴇᴍ Dɪsᴘʟᴀʏ Mᴏᴅᴇ**\n\nSelect a rarity to filter your /harem:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^wmset_"))
async def set_wmode(client, query: CallbackQuery):
    mode = query.data.split("_")[1]
    await users.update_one(
        {"_id": query.from_user.id},
        {"$set": {"harem_mode": mode}},
        upsert=True
    )
    await query.answer(f"✅ Harem filter set to {mode}")
    await query.message.edit_text(f"✅ Your `/harem` now shows: **{mode.upper()}**")