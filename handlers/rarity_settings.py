from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import settings 
from config import OWNER_ID

# Updated with all 17 Rarities
RARITIES_MAP = {
    "Common": "⚪️",
    "Legendary": "💮",
    "Rare": "🍁",
    "Special": "🫧",
    "Limited": "🔮",
    "Celestial": "🎐",
    "Manga": "🔖",
    "Expensive": "💸",
    "Demonic": "☠",
    "Royal": "👑",
    "Summer": "🏝️",
    "Winter": "❄️",
    "Valentine": "💝",
    "Seasonal": "🍂",
    "Halloween": "🎃",
    "Christmas": "🎄",
    "AMV": "🎥"
}

async def get_global_rarities():
    """Fetches the single global list of allowed rarities"""
    data = await settings.find_one({"_id": "global_spawn_settings"})
    if not data or "rarities" not in data:
        # Default: All enabled if first time
        return list(RARITIES_MAP.keys())
    return data["rarities"]

@Client.on_message(filters.command("rarity"), group=-1)
async def rarity_settings_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Access Denied: Owner Only.**")

    allowed = await get_global_rarities()
    
    text = (
        f"🌍 **Gʟᴏʙᴀʟ Sᴘᴀᴡɴ Cᴏɴᴛʀᴏʟ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 **Status:** Affected rarities will **NOT** spawn in any GC.\n"
        f"✅ = Allowed | ❌ = Locked\n\n"
        f"**Toggle Rarities:**"
    )

    buttons = []
    rarity_keys = list(RARITIES_MAP.keys())
    # Create buttons in rows of 2
    for i in range(0, len(rarity_keys), 2):
        row = []
        for r_name in rarity_keys[i:i+2]:
            emoji = RARITIES_MAP[r_name]
            status = "✅" if r_name in allowed else "❌"
            row.append(InlineKeyboardButton(
                f"{emoji} {r_name} {status}", 
                callback_data=f"global_tr_{r_name}"
            ))
        buttons.append(row)
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^global_tr_"))
async def toggle_global_rarity(client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("🛑 Owner Only!", show_alert=True)

    r_name = query.data.split("_")[2]
    allowed = await get_global_rarities()
    allowed = list(allowed)

    if r_name in allowed:
        allowed.remove(r_name)
    else:
        allowed.append(r_name)

    await settings.update_one(
        {"_id": "global_spawn_settings"}, 
        {"$set": {"rarities": allowed}}, 
        upsert=True
    )

    # Rebuild UI
    buttons = []
    rarity_keys = list(RARITIES_MAP.keys())
    for i in range(0, len(rarity_keys), 2):
        row = []
        for name in rarity_keys[i:i+2]:
            emoji = RARITIES_MAP[name]
            status = "✅" if name in allowed else "❌"
            row.append(InlineKeyboardButton(
                f"{emoji} {name} {status}", 
                callback_data=f"global_tr_{name}"
            ))
        buttons.append(row)

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await query.answer(f"Updated: {r_name}")