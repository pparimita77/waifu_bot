import random
import html
import pytz
from datetime import datetime, timezone
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, InputMediaVideo
from database import db, characters, users, claims, settings
from config import OWNER_ID, DEVS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- CONFIGURATION & PERMISSIONS ---
def flatten_ids(owner, devs):
    ids = {int(x) for x in (owner if isinstance(owner, list) else [owner]) if x}
    if devs:
        ids.update(int(x) for x in (devs if isinstance(devs, list) else [devs]) if x)
    return list(ids)

AUTHORIZED = flatten_ids(OWNER_ID, DEVS)

RARITY_MAP = {
    "1": ("Common", "⚪️"), "2": ("Legendary", "💮"), "3": ("Rare", "🍁"),
    "4": ("Special", "🫧"), "5": ("Limited", "🔮"), "6": ("Celestial", "🎐"),
    "7": ("Manga", "🔖"), "8": ("Expensive", "💸"), "9": ("Demonic", "☠"),
    "10": ("Royal", "👑"), "11": ("Summer", "🏝️"), "12": ("Winter", "❄️"),
    "13": ("Valentine", "💝"), "14": ("Seasonal", "🍂"), "15": ("Halloween", "🎃"),
    "16": ("Christmas", "🎄"), "17": ("AMV", "🎥")
}

# --- ⏰ AUTO-REFRESH LOGIC ---
async def refresh_shop_data():
    await settings.delete_one({"type": "daily_shop"})

scheduler = AsyncIOScheduler(timezone=pytz.timezone("UTC"))
scheduler.add_job(refresh_shop_data, "cron", hour=0, minute=0)
scheduler.start()

# --- UTILITIES ---
async def get_user_data(uid):
    return await users.find_one({"$or": [{"user_id": uid}, {"_id": uid}]})

# --- 🛒 SHOP GENERATION ---
async def get_daily_shop():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily = await settings.find_one({"type": "daily_shop"})
    
    if daily and daily.get("date") == today:
        return daily.get("items")

    # Fetch configuration
    config = await settings.find_one({"type": "allowed_rarities"})
    allowed_ids = config.get("list", []) if config else ["1"]
    allowed_names = [RARITY_MAP[i][0] for i in allowed_ids if i in RARITY_MAP]
    
    active_auc = await db.auctions.find_one({"_id": "active"})
    excl_id = active_auc.get("char_id") if active_auc else None

    match_filter = {"rarity": {"$regex": f"^({'|'.join(allowed_names)})", "$options": "i"}}
    if excl_id: match_filter["id"] = {"$ne": excl_id}

    # Fetch 3 random characters
    chars = await characters.aggregate([{"$match": match_filter}, {"$sample": {"size": 3}}]).to_list(3)
    
    shop_items = []
    for char in chars:
        # Determine rarity ID based on character rarity string
        r_id = next((k for k, v in RARITY_MAP.items() if v[0].lower() in char.get("rarity", "").lower()), "1")
        p_cfg = await settings.find_one({"type": "rarity_config", "rarity_id": str(r_id)})
        min_p, max_p = (p_cfg.get("min", 50), p_cfg.get("max", 200)) if p_cfg else (50, 200)
        
        shop_items.append({
            "char": char, 
            "price": random.randint(min_p, max_p), 
            "r_id": r_id
        })

    await settings.update_one(
        {"type": "daily_shop"}, 
        {"$set": {"date": today, "items": shop_items}}, 
        upsert=True
    )
    return shop_items

# --- UI HANDLERS ---

@Client.on_message(filters.command("shop"))
async def shop_cmd(client, message):
    items = await get_daily_shop()
    if not items: return await message.reply_text("🙇 Shop is empty!")
    user = await get_user_data(message.from_user.id)
    await show_waifu(client, message, items, 0, user.get("emeralds", 0) if user else 0, owner_id=message.from_user.id)

async def show_waifu(client, event, items, index, balance, is_cb=False, owner_id=None):
    total = len(items)
    index %= total
    item = items[index]
    char, price, r_id = item['char'], item['price'], item['r_id']
    
    is_video = "amv" in char.get('rarity', '').lower() or char.get("is_video", False)
    file_id = char.get('file_id') or char.get('image')

    text = (
        f"🌸 <b>Dᴀɪʟʏ Sʜᴏᴘ - [{index + 1}/{total}]</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Nᴀᴍᴇ:</b> {html.escape(char['name'])}\n"
        f"{RARITY_MAP[r_id][1]} <b>Rᴀʀɪᴛʏ:</b> {RARITY_MAP[r_id][0]}\n"
        f"💰 <b>Cᴏsᴛ:</b> {price:,} 💠\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👛 <b>Bᴀʟᴀɴᴄᴇ:</b> {balance:,} 💠"
    )
    
    # Callback data optimized to avoid 64-char limit
    btns = [[InlineKeyboardButton(f"🛒 BUY {price} 💠", callback_data=f"buy_{index}_{owner_id}")]]
    if total > 1:
        btns.append([
            InlineKeyboardButton("⬅️ Prev", callback_data=f"nav_{index-1}_{owner_id}"), 
            InlineKeyboardButton("Next ➡️", callback_data=f"nav_{index+1}_{owner_id}")
        ])
    
    markup = InlineKeyboardMarkup(btns)
    if is_cb:
        media = InputMediaVideo(file_id, caption=text) if is_video else InputMediaPhoto(file_id, caption=text)
        await event.edit_message_media(media, reply_markup=markup)
    else:
        await (event.reply_video(file_id, caption=text, reply_markup=markup) if is_video 
               else event.reply_photo(file_id, caption=text, reply_markup=markup))

@Client.on_callback_query(filters.regex(r"^(nav_|buy_|tr_|force_refresh_shop)"))
async def handle_callbacks(client, query: CallbackQuery):
    data = query.data.split("_")
    uid = query.from_user.id
    
    # Permission Check
    if data[0] in ["nav", "buy"]:
        if uid != int(data[-1]):
            return await query.answer("🚫 Not your menu!", show_alert=True)

    items = await get_daily_shop()

    if query.data.startswith("nav_"):
        user = await get_user_data(uid)
        await show_waifu(client, query, items, int(data[1]), user.get("emeralds", 0) if user else 0, is_cb=True, owner_id=uid)

    elif query.data.startswith("buy_"):
        idx = int(data[1])
        item = items[idx]
        char, price = item['char'], item['price']
        
        # Atomically check and deduct emeralds
        user_update = await users.find_one_and_update(
            {"$or": [{"user_id": uid}, {"_id": uid}], "emeralds": {"$gte": price}},
            {"$inc": {"emeralds": -price}}
        )
        
        if not user_update:
            return await query.answer("❌ Insufficient Emeralds!", show_alert=True)
            
        if await claims.find_one({"user_id": uid, "char_id": char['id']}):
            # Refund if already owned (Safety fallback)
            await users.update_one({"_id": user_update["_id"]}, {"$inc": {"emeralds": price}})
            return await query.answer("⚠️ Already owned!", show_alert=True)

        # Success: Add full data to claims
        await claims.insert_one({
            "user_id": uid,
            "char_id": char['id'],
            "name": char['name'],
            "rarity": char['rarity'],
            "anime": char.get('anime', 'Unknown'),
            "date": datetime.now(timezone.utc)
        })
        
        await query.answer("✅ Purchased!", show_alert=True)
        await query.message.edit_caption(
            caption=f"🛍️ <b>Purchase Successful!</b>\n\nCharacter: <b>{char['name']}</b>\nSpent: {price:,} 💠",
            reply_markup=None
        )

    elif query.data.startswith("tr_") or query.data == "force_refresh_shop":
        if uid not in AUTHORIZED: return await query.answer("Denied.")
        # ... logic for rarity toggle and refresh ...
        if query.data == "force_refresh_shop":
            await refresh_shop_data()
            await query.answer("Shop Refreshed!", show_alert=True)
