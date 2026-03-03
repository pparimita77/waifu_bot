import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from database import characters, shop_config, users, claims

# 1. OWNER ID
OWNER_ID = 8325139144 

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
        return await message.reply_text("❌ **Usage:** `/setcost <no> <min> <max>`\nExample: `/setcost 1 50 100` (Sets Common to 50-100 Krytos)")
    
    try:
        idx = int(message.command[1]) - 1
        r_min = int(message.command[2])
        r_max = int(message.command[3])
        
        if not (0 <= idx < len(RARITY_DATA)):
            return await message.reply_text(f"❌ Invalid Rarity Number! Use 1-{len(RARITY_DATA)}.")
            
        name = RARITY_DATA[idx][0]
        
        # Save to database under the 'costs' document
        await shop_config.update_one(
            {"id": "costs"}, 
            {"$set": {name: {"min": r_min, "max": r_max}}}, 
            upsert=True
        )
        
        await message.reply_text(f"✅ **{name}** Krytos Price Updated: `💎 {r_min:,}` - `💎 {r_max:,}`")
        
    except ValueError:
        await message.reply_text("❌ Error: Min and Max prices must be numbers!")

# --- 2. THE BUY SYSTEM (Krytos Sync) ---

@Client.on_callback_query(filters.regex(r"^buy_"))
async def buy_handler(client, query):
    data = query.data.split("_")
    char_id, cost = data[1], int(data[2])
    user_id = query.from_user.id

    # Fetch user from your main database
    user = await users.find_one({"user_id": user_id})
    
    # Check Krytos Balance
    user_krytos = user.get("krytos", 0) if user else 0

    if user_krytos < cost:
        return await query.answer(f"❌ Not enough Krytos! You need {cost - user_krytos} ₭ more.", show_alert=True)

    # Check if user already owns character
    check = await claims.find_one({"user_id": user_id, "char_id": char_id})
    if check:
        return await query.answer("⚠️ You already own this character!", show_alert=True)

    # Deduct Krytos and Add to Collection
    await users.update_one({"user_id": user_id}, {"$inc": {"krytos": -cost}})
    await claims.insert_one({"user_id": user_id, "char_id": char_id})
    
    await query.message.edit_caption(
        caption=f"🎉 **Purchase Successful!**\n\nCharacter `{char_id}` has been added to your collection.\n💎 **Spent:** `{cost:,}` Krytos.",
        reply_markup=None
    )
    await query.answer("Successfully added to collection!")

# --- 3. THE USER SHOP DISPLAY ---

async def show_item(event, rarity_name, is_cb=False):
    # Fetch random character matching rarity
    char_list = await characters.aggregate([
        {"$match": {"rarity": {"$regex": f"^{rarity_name}", "$options": "i"}}},
        {"$sample": {"size": 1}}
    ]).to_list(1)

    if not char_list:
        msg = f"❌ No characters found for {rarity_name}."
        return await (event.answer(msg, show_alert=True) if is_cb else event.reply_text(msg))

    char = char_list[0]
    
    # Get costs set by /setcost
    costs_doc = await shop_config.find_one({"id": "costs"}) or {}
    r_range = costs_doc.get(rarity_name, {"min": 100, "max": 200}) # Default if not set
    price = random.randint(r_range['min'], r_range['max'])
    
    emoji = next((e for n, e in RARITY_DATA if n == rarity_name), "💎")
    caption = (
        f"🛍️ **Pɪʀᴀᴛᴇ Sʜᴏᴘ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 **Name:** {char['name']}\n"
        f"🔺 **Anime:** {char['anime']}\n"
        f"💡 **Rarity:** {emoji} {rarity_name}\n"
        f"💎 **Price:** `{price:,}` Krytos\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{char['id']}`"
    )

    # Navigation logic
    vis = await shop_config.find_one({"id": "visibility"})
    active = vis.get("active_buttons", [rarity_name])
    idx = active.index(rarity_name) if rarity_name in active else 0
    
    prev_r = active[idx - 1] if idx > 0 else active[-1]
    next_r = active[idx + 1] if idx < len(active) - 1 else active[0]

    buttons = [
        [InlineKeyboardButton(f"🛒 Buy for {price:,} ₭", callback_data=f"buy_{char['id']}_{price}")],
        [
            InlineKeyboardButton("⬅️ Previous", callback_data=f"sh_nav_{prev_r}"),
            InlineKeyboardButton("Next ➡️", callback_data=f"sh_nav_{next_r}")
        ]
    ]

    if is_cb:
        await event.message.edit_media(InputMediaPhoto(char['file_id'], caption=caption), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await event.reply_photo(photo=char['file_id'], caption=caption, reply_markup=InlineKeyboardMarkup(buttons))