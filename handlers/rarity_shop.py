import random
import html
import pytz  # NEW: Added for Scheduler fix
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, InputMediaVideo
from pyrogram.enums import ParseMode
from database import db, characters, users, claims, settings
from config import OWNER_ID, DEVS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- CONFIGURATION & PERMISSIONS ---
def flatten_ids(owner, devs):
    flat_list = []
    # Handle Owner ID (can be int or list)
    if isinstance(owner, list):
        flat_list.extend(owner)
    else:
        flat_list.append(owner)
    
    # Handle Devs (can be None, int, or list)
    if devs:
        if isinstance(devs, list):
            flat_list.extend(devs)
        else:
            flat_list.append(devs)
            
    # Remove duplicates and ensure all are integers
    return list(set(int(x) for x in flat_list if x))

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

# FIX: Added timezone=pytz.timezone("UTC") to solve the Windows/Python 3.12 crash
scheduler = AsyncIOScheduler(timezone=pytz.timezone("UTC"))
scheduler.add_job(refresh_shop_data, "cron", hour=0, minute=0)
scheduler.start()

# --- UTILITIES ---
async def get_user_bal(uid):
    user = await users.find_one({"$or": [{"user_id": uid}, {"_id": uid}]})
    if user: return user.get("emeralds", 0), user.get("_id")
    return 0, None

# --- 🛒 SHOP GENERATION ---
async def get_daily_shop():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily = await settings.find_one({"type": "daily_shop"})
    
    active_auc = await db.auctions.find_one({"_id": "active"})
    excl_id = active_auc.get("char_id") if active_auc else None

    if not daily or daily.get("date") != today:
        config = await settings.find_one({"type": "allowed_rarities"})
        allowed_ids = config.get("list", []) if config else []
        allowed_names = [RARITY_MAP[i][0] for i in allowed_ids if i in RARITY_MAP]

        shop_items = []
        
        if allowed_names:
            pattern = f"^({'|'.join(allowed_names)})"
            match_filter = {"rarity": {"$regex": pattern, "$options": "i"}}
        else:
            match_filter = {"rarity": {"$regex": "^Common", "$options": "i"}}

        if excl_id:
            match_filter["id"] = {"$ne": excl_id}

        chars = await characters.aggregate([
            {"$match": match_filter},
            {"$sample": {"size": 3}}
        ]).to_list(3)

        for char in chars:
            r_id = next((k for k, v in RARITY_MAP.items() if v[0].lower() in char.get("rarity", "").lower()), "1")
            p_cfg = await settings.find_one({"type": "rarity_config", "rarity_id": str(r_id)})
            min_p, max_p = (p_cfg.get("min", 50), p_cfg.get("max", 200)) if p_cfg else (50, 200)
            
            shop_items.append({
                "char": char, 
                "price": random.randint(min_p, max_p), 
                "r_id": r_id
            })

        if len(shop_items) < 3:
            needed = 3 - len(shop_items)
            f_match = {"rarity": {"$regex": "^Common", "$options": "i"}}
            if excl_id: f_match["id"] = {"$ne": excl_id}
            fillers = await characters.aggregate([{"$match": f_match}, {"$sample": {"size": needed}}]).to_list(needed)
            for char in fillers:
                shop_items.append({"char": char, "price": random.randint(50, 100), "r_id": "1"})

        await settings.update_one(
            {"type": "daily_shop"}, 
            {"$set": {"date": today, "items": shop_items}}, 
            upsert=True
        )
        return shop_items
        
    return daily.get("items")

# --- UI HANDLERS ---

@Client.on_message(filters.command("shop_rarity") & filters.user(AUTHORIZED))
async def shop_rarity_cmd(client, message):
    config = await settings.find_one({"type": "allowed_rarities"}) or {"list": []}
    allowed = config.get("list", [])
    btns = []
    row = []
    
    for r_id in sorted(RARITY_MAP.keys(), key=int):
        status = "✅" if r_id in allowed else "❌"
        row.append(InlineKeyboardButton(f"{status} {RARITY_MAP[r_id][0]}", callback_data=f"tr_{r_id}"))
        if len(row) == 2:
            btns.append(row)
            row = []
    if row: btns.append(row)
    btns.append([InlineKeyboardButton("♻️ FORCE REFRESH SHOP", callback_data="force_refresh_shop")])
    
    await message.reply_text("⚙️ <b>Sʜᴏᴘ Rᴀʀɪᴛʏ Cᴏɴᴛʀᴏʟ Pᴀɴᴇʟ</b>", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_message(filters.command("shop"))
async def shop_cmd(client, message):
    items = await get_daily_shop()
    if not items: return await message.reply_text("🙇 Shop is currently empty!")
    bal, _ = await get_user_bal(message.from_user.id)
    await show_waifu(client, message, items, 0, bal, owner_id=message.from_user.id)

async def show_waifu(client, event, items, index, balance, is_cb=False, owner_id=None):
    total = len(items)
    index = index % total
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
        f"👛 <b>Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ:</b> {balance:,} 💠"
    )
    
    btns = [[InlineKeyboardButton(f"🛒 BUY FOR {price:,} 💠", callback_data=f"buy_{char['id']}_{price}_{owner_id}")]]
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
        if is_video: await event.reply_video(video=file_id, caption=text, reply_markup=markup)
        else: await event.reply_photo(photo=file_id, caption=text, reply_markup=markup)

@Client.on_callback_query(filters.regex(r"^(nav_|buy_|tr_|force_refresh_shop)"))
async def handle_callbacks(client, query: CallbackQuery):
    data_parts = query.data.split("_")
    uid = query.from_user.id
    
    if data_parts[0] in ["nav", "buy"]:
        owner_id = int(data_parts[-1])
        if uid != owner_id:
            return await query.answer("🚫 This is not your menu!", show_alert=True)

    if query.data.startswith("nav_"):
        items = await get_daily_shop()
        idx = int(data_parts[1])
        bal, _ = await get_user_bal(uid)
        await show_waifu(client, query, items, idx, bal, is_cb=True, owner_id=uid)

    elif query.data.startswith("tr_"):
        if uid not in AUTHORIZED: return
        r_id = data_parts[1]
        config = await settings.find_one({"type": "allowed_rarities"}) or {"list": []}
        allowed = list(config.get("list", []))
        if r_id in allowed: allowed.remove(r_id)
        else: allowed.append(r_id)
        await settings.update_one({"type": "allowed_rarities"}, {"$set": {"list": allowed}}, upsert=True)
        # Update current panel without deleting (to avoid flicker)
        await shop_rarity_cmd(client, query.message)
        await query.message.delete()

    elif query.data == "force_refresh_shop":
        if uid not in AUTHORIZED: return
        await refresh_shop_data()
        await query.answer("♻️ Shop Refreshed! Open /shop again.", show_alert=True)

    elif query.data.startswith("buy_"):
        cid, price = data_parts[1], int(data_parts[2])
        bal, mongo_id = await get_user_bal(uid)
        
        if bal < price: return await query.answer("❌ Not enough Emeralds!", show_alert=True)
        if await claims.find_one({"user_id": uid, "char_id": cid}): 
            return await query.answer("⚠️ Already owned!", show_alert=True)

        await users.update_one({"_id": mongo_id}, {"$inc": {"emeralds": -price}})
        await claims.insert_one({"user_id": uid, "char_id": cid, "id": cid, "date": datetime.utcnow()})
        await query.answer("✅ Purchased!", show_alert=True)
        await query.message.edit_caption(caption=f"🛍️ <b>Purchase Successful!</b>\n\nYou bought this character for {price:,} 💠.")