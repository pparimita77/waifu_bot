import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from database import characters, shop_config

# This list must be present in this file too
RARITY_DATA = [
    ("Common", "⚪️"), ("Legendary", "💮"), ("Rare", "🏵"), ("Special", "🫧"),
    ("Limited", "🔮"), ("Celestial", "🎐"), ("Manga", "🔖"), ("Expensive", "💸"),
    ("Giveaway", "🧧"), ("Seasonal", "🍂"), ("Valentine", "💝"), ("AMV", "🎥")
]

@Client.on_message(filters.command("shop"))
async def open_shop(client, message):
    vis = await shop_config.find_one({"id": "visibility"})
    active = vis.get("active_buttons", ["Common"]) if vis else ["Common"]
    await show_shop_item(message, active[0], is_cb=False)

@Client.on_callback_query(filters.regex(r"^sh_nav_"))
async def shop_callback(client, query):
    rarity = query.data.split("_")[-1]
    await show_shop_item(query, rarity, is_cb=True)

async def show_shop_item(event, rarity, is_cb=False):
    # This regex ensures "common", "Common", and "COMMON" all work
    query_filter = {"rarity": {"$regex": f"^{rarity}$", "$options": "i"}}
    
    char_list = await characters.aggregate([
        {"$match": query_filter}, 
        {"$sample": {"size": 1}}
    ]).to_list(1)

    if not char_list:
        msg = f"❌ DB Error: No characters found matching rarity '{rarity}'. Check your character database spelling!"
        return await (event.answer(msg, show_alert=True) if is_cb else event.reply_text(msg))

    char = char_list[0]
    costs = await shop_config.find_one({"id": "costs"}) or {}
    r_range = costs.get(rarity, {"min": 5000, "max": 10000})
    price = random.randint(r_range['min'], r_range['max'])
    
    emoji = next((e for n, e in RARITY_DATA if n == rarity), "💠")
    
    caption = (
        f"🛍️ **Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ Sʜᴏᴘ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 **Name:** {char['name']}\n"
        f"💡 **Rarity:** {emoji} {rarity}\n"
        f"💸 **Price:** `{price:,}` 💠 Emeralds\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{char['id']}`"
    )

    # Navigation Logic
    vis = await shop_config.find_one({"id": "visibility"})
    active = vis.get("active_buttons", [rarity])
    idx = active.index(rarity) if rarity in active else 0
    prev_r = active[idx - 1] if idx > 0 else active[-1]
    next_r = active[idx + 1] if idx < len(active) - 1 else active[0]

    buttons = [
        [InlineKeyboardButton(f"🛒 Buy for {price:,} 💠", callback_data=f"buy_{char['id']}_{price}")],
        [
            InlineKeyboardButton(f"⬅️ {prev_r}", callback_data=f"sh_nav_{prev_r}"),
            InlineKeyboardButton(f"{next_r} ➡️", callback_data=f"sh_nav_{next_r}")
        ],
        [InlineKeyboardButton("🔄 Next Character", callback_data=f"sh_nav_{rarity}")]
    ]

    if is_cb:
        await event.message.edit_media(InputMediaPhoto(char['file_id'], caption=caption), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await event.reply_photo(photo=char['file_id'], caption=caption, reply_markup=InlineKeyboardMarkup(buttons))