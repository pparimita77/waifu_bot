from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import shop_config

# ⚠️ YOUR TELEGRAM ID
OWNER_ID = 123456789 

RARITY_DATA = [
    ("Common", "⚪️"), ("Legendary", "💮"), ("Rare", "🏵"), ("Special", "🫧"),
    ("Limited", "🔮"), ("Celestial", "🎐"), ("Manga", "🔖"), ("Expensive", "💸"),
    ("Giveaway", "🧧"), ("Seasonal", "🍂"), ("Valentine", "💝"), ("AMV", "🎥")
]

@Client.on_message(filters.command("shoprarity") & filters.user(OWNER_ID))
async def shop_rarity_manager(client, message):
    vis = await shop_config.find_one({"id": "visibility"})
    active = vis.get("active_buttons", []) if vis else []

    text = "🛠️ **Sʜᴏᴘ Rᴀʀɪᴛʏ Mᴀɴᴀɢᴇʀ**\n\nTap buttons to toggle visibility in `/shop`."
    
    buttons = []
    row = []
    for name, emoji in RARITY_DATA:
        status = "✅" if name in active else "❌"
        # Prefix 'tr_' must match the handler below
        row.append(InlineKeyboardButton(f"{status} {emoji} {name}", callback_data=f"tr_{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("🌟 ENABLE ALL", callback_data="tr_allon"),
        InlineKeyboardButton("🗑️ DISABLE ALL", callback_data="tr_alloff")
    ])

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- BUTTON HANDLER (This must be active) ---
@Client.on_callback_query(filters.regex(r"^tr_"))
async def handle_rarity_toggle(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("❌ Owner Only!", show_alert=True)

    vis = await shop_config.find_one({"id": "visibility"})
    active = vis.get("active_buttons", []) if vis else []
    data = query.data.replace("tr_", "")
    
    if data == "allon":
        active = [r[0] for r in RARITY_DATA]
    elif data == "alloff":
        active = []
    else:
        if data in active:
            active.remove(data)
        else:
            active.append(data)

    await shop_config.update_one(
        {"id": "visibility"},
        {"$set": {"active_buttons": active}},
        upsert=True
    )

    # RE-BUILD THE MENU TO REFRESH
    buttons = []
    row = []
    for name, emoji in RARITY_DATA:
        status = "✅" if name in active else "❌"
        row.append(InlineKeyboardButton(f"{status} {emoji} {name}", callback_data=f"tr_{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([
        InlineKeyboardButton("🌟 ENABLE ALL", callback_data="tr_allon"),
        InlineKeyboardButton("🗑️ DISABLE ALL", callback_data="tr_alloff")
    ])

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await query.answer("Settings Updated!")