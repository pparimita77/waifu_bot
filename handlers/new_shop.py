import random
import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from database import characters, shop_config, users, claims

# 1. OWNER ID
OWNER_ID = 7987799736

# Master Rarity List
RARITY_DATA = [
    ("Common", "⚪️"), ("Legendary", "💮"), ("Rare", "🍁"), ("Special", "🫧"),
    ("Limited", "🔮"), ("Celestial", "🎐"), ("Manga", "🔖"), ("Expensive", "💸"),
    ("Giveaway", "🧧"), ("Royal", "👑"), ("Summer", "🏝️"), ("Winter", "❄️"),
    ("Valentine", "💝"), ("Seasonal", "🍂"), ("Halloween", "🎃"), ("Christmas", "🎄"), ("AMV", "🎥")
]

# --- 1. MANAGEMENT COMMANDS ---

@Client.on_message(filters.command("setcost"))
async def set_cost(client, message):
    if message.from_user.id != OWNER_ID: return
    
    if len(message.command) < 4:
        return await message.reply_text("❌ **Usage:** `/setcost <no> <min> <max>`\nExample: `/setcost 1 50 100` (Sets Common)")
    
    try:
        idx = int(message.command[1]) - 1
        r_min, r_max = int(message.command[2]), int(message.command[3])
        
        if not (0 <= idx < len(RARITY_DATA)):
            return await message.reply_text(f"❌ Invalid Rarity Number!")
            
        name = RARITY_DATA[idx][0]
        await shop_config.update_one(
            {"id": "costs"}, 
            {"$set": {name: {"min": r_min, "max": r_max}}}, 
            upsert=True
        )
        await message.reply_text(f"✅ **{name}** Price Updated: `💎 {r_min:,}` - `💎 {r_max:,}`")
    except ValueError:
        await message.reply_text("❌ Prices must be numbers!")

# --- 2. THE BUY SYSTEM ---

@Client.on_callback_query(filters.regex(r"^buy_"))
async def buy_handler(client, query):
    data = query.data.split("_")
    char_id, cost = data[1], int(data[2])
    user_id = query.from_user.id

    user = await users.find_one({"user_id": user_id}) or {}
    if user.get("krytos", 0) < cost:
        return await query.answer(f"❌ Not enough Krytos!", show_alert=True)

    # Check ownership
    if await claims.find_one({"user_id": user_id, "char_id": char_id}):
        return await query.answer("⚠️ You already own this character!", show_alert=True)

    # Fetch character data to save full info for /harem
    char = await characters.find_one({"id": char_id})
    if not char:
        return await query.answer("❌ Character no longer exists!", show_alert=True)

    # Deduct & Add
    await users.update_one({"user_id": user_id}, {"$inc": {"krytos": -cost}})
    await claims.insert_one({
        "user_id": user_id,
        "char_id": char['id'],
        "name": char['name'],
        "rarity": char['rarity'],
        "anime": char.get('anime') or "Unknown",
        "date": datetime.datetime.now()
    })
    
    await query.message.edit_caption(
        caption=f"🎉 **Purchase Successful!**\n\nCharacter: **{char['name']}**\n💎 **Spent:** `{cost:,}` Krytos.",
        reply_markup=None
    )
    await query.answer("Successfully added to collection!")

# --- 3. THE DISPLAY LOGIC ---

async def show_item(event, rarity_name, is_cb=False):
    char_list = await characters.aggregate([
        {"$match": {"rarity": {"$regex": f"^{rarity_name}", "$options": "i"}}},
        {"$sample": {"size": 1}}
    ]).to_list(1)

    if not char_list:
        msg = f"❌ No characters found for {rarity_name}."
        return await (event.answer(msg, show_alert=True) if is_cb else event.reply_text(msg))

    char = char_list[0]
    
    # Correct Media Handling
    media_id = char.get('file_id') or char.get('img_url') or char.get('image')
    is_video = "amv" in str(char.get('rarity', '')).lower() or char.get("is_video", False)

    costs_doc = await shop_config.find_one({"id": "costs"}) or {}
    r_range = costs_doc.get(rarity_name, {"min": 100, "max": 200})
    price = random.randint(r_range['min'], r_range['max'])
    
    emoji = next((e for n, e in RARITY_DATA if n == rarity_name), "💎")
    caption = (
        f"🛍️ **Tomioka Sʜᴏᴘ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 **Name:** {char['name']}\n"
        f"🔺 **Anime:** {char['anime']}\n"
        f"💡 **Rarity:** {emoji} {rarity_name}\n"
        f"💎 **Price:** `{price:,}` Krytos\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{char['id']}`"
    )

    # Navigation Logic (Fallback to RARITY_DATA if visibility doc missing)
    vis = await shop_config.find_one({"id": "visibility"})
    active = vis.get("active_buttons", [r[0] for r in RARITY_DATA]) if vis else [r[0] for r in RARITY_DATA]
    
    idx = active.index(rarity_name) if rarity_name in active else 0
    prev_r = active[idx - 1] if idx > 0 else active[-1]
    next_r = active[idx + 1] if idx < len(active) - 1 else active[0]

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🛒 Buy for {price:,} ₭", callback_data=f"buy_{char['id']}_{price}")],
        [
            InlineKeyboardButton("⬅️ Prev", callback_data=f"sh_nav_{prev_r}"),
            InlineKeyboardButton("Next ➡️", callback_data=f"sh_nav_{next_r}")
        ]
    ])

    try:
        if is_cb:
            media = InputMediaVideo(media_id, caption=caption) if is_video else InputMediaPhoto(media_id, caption=caption)
            await event.message.edit_media(media, reply_markup=buttons)
        else:
            if is_video:
                await event.reply_video(video=media_id, caption=caption, reply_markup=buttons)
            else:
                await event.reply_photo(photo=media_id, caption=caption, reply_markup=buttons)
    except Exception:
        await event.reply_text(caption, reply_markup=buttons)

# --- 4. LISTENERS ---

@Client.on_message(filters.command("shop"))
async def shop_cmd(client, message):
    await show_item(message, "Common", is_cb=False)

@Client.on_callback_query(filters.regex(r"^sh_nav_"))
async def shop_nav(client, query):
    rarity = query.data.split("_")[2]
    await show_item(query, rarity, is_cb=True)
