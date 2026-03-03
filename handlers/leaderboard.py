import html
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from database import db, users, claims  # Ensure these are imported correctly

# --- 🛠️ HELPER: NAME RESOLVER ---
async def get_user_name(client, user_id):
    """Fetches name from DB or Telegram API with a timeout to prevent hanging."""
    try:
        u_id = int(user_id)
        # 1. Check database cache
        user_info = await users.find_one({"$or": [{"_id": u_id}, {"user_id": u_id}]})
        if user_info and user_info.get("first_name"):
            return user_info["first_name"]
        
        # 2. Fetch from Telegram (2 second timeout)
        user_obj = await asyncio.wait_for(client.get_users(u_id), timeout=2.0)
        if user_obj and user_obj.first_name:
            name = user_obj.first_name
            # Save to DB for next time
            await users.update_one({"user_id": u_id}, {"$set": {"first_name": name}}, upsert=True)
            return name
    except:
        pass
    return f"Player {str(user_id)[-4:]}"

# --- 📊 CORE LOGIC: LEADERBOARD TEXT ---
async def get_top_text(client, category, user_id, chat_id=None, timeframe="all"):
    now = datetime.utcnow()
    match_f = {}
    
    # Timeframe Labeling
    labels = {"weekly": " (Wᴇᴇᴋʟʏ)", "monthly": " (Mᴏɴᴛʜʟʏ)", "all": " (Aʟʟ-Tɪᴍᴇ)"}
    time_label = labels.get(timeframe, " (Aʟʟ-Tɪᴍᴇ)")

    if timeframe == "weekly":
        match_f["date"] = {"$gte": now - timedelta(days=7)}
    elif timeframe == "monthly":
        match_f["date"] = {"$gte": now - timedelta(days=30)}

    # Category Mapping
    titles = {"stardust": "🌟 Sᴛᴀʀᴅᴜsᴛ", "emerald": "💠 Eᴍᴇʀᴀʟᴅ", "guesser": "🧠 Gᴜᴇssᴇʀs", "chars": "🎴 Cᴏʟʟᴇᴄᴛᴏʀs"}
    keys = {"stardust": "stardust", "emerald": "emeralds", "guesser": "guesses", "chars": "waifus"}
    
    title = titles.get(category, "🏆 Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ")
    key = keys.get(category, "count")

    text = f"🏆 <b>Tᴏᴘ 10 {title}</b>{time_label}\n"
    text += f"{'👥 Gʀᴏᴜᴘ' if chat_id else '🌍 Gʟᴏʙᴀʟ'}\n━━━━━━━━━━━━━━━━━━━━\n"

    results = []
    # 1. Fetch from Collections (Claims/Guesses)
    if category in ["chars", "guesser"]:
        col = claims if category == "chars" else db.guesses 
        if chat_id: match_f["last_chat_id"] = chat_id
        
        pipeline = [
            {"$match": match_f},
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = await col.aggregate(pipeline).to_list(10)
    
    # 2. Fetch from User Documents (Currency)
    else:
        q_filter = {key: {"$gt": 0}}
        if chat_id: q_filter["last_chat_id"] = chat_id
        cursor = users.find(q_filter).sort(key, -1).limit(10)
        async for d in cursor:
            results.append({"_id": d.get("user_id") or d.get("_id"), "count": d.get(key, 0)})

    # Fetch names in parallel for speed
    tasks = [get_user_name(client, res["_id"]) for res in results]
    names = await asyncio.gather(*tasks)

    for i, (data, name) in enumerate(zip(results, names), 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"<b>{i}.</b>"
        text += f"{medal} <a href='tg://user?id={data['_id']}'>{html.escape(name)}</a> — <code>{data['count']:,}</code>\n"

    if not results:
        text += "<i>No data found yet...</i>\n"

    # --- 👤 PERSONAL RANK CALCULATION ---
    try:
        if category in ["chars", "guesser"]:
            col = claims if category == "chars" else db.guesses
            u_val = await col.count_documents({"user_id": user_id, **match_f})
            rank_pipe = [{"$match": match_f}, {"$group": {"_id": "$user_id", "count": {"$sum": 1}}}, {"$match": {"count": {"$gt": u_val}}}, {"$count": "total"}]
            r_res = await col.aggregate(rank_pipe).to_list(1)
            u_rank = (r_res[0]["total"] + 1) if r_res else 1
        else:
            u_data = await users.find_one({"$or": [{"_id": user_id}, {"user_id": user_id}]})
            u_val = u_data.get(key, 0) if u_data else 0
            u_rank = await users.count_documents({key: {"$gt": u_val}}) + 1
    except:
        u_val, u_rank = 0, "?"

    text += f"━━━━━━━━━━━━━━━━━━━━\n👤 <b>Yᴏᴜʀ Rᴀɴᴋ:</b> <code>#{u_rank}</code> (<code>{u_val:,}</code>)"
    return text

# --- 🔘 BUTTON BUILDER ---
def get_top_buttons(category, mode="global", timeframe="all"):
    btns = [[
        InlineKeyboardButton("🌟 Star", callback_data=f"t_cat_stardust_{mode}_{timeframe}"),
        InlineKeyboardButton("💠 Eme", callback_data=f"t_cat_emerald_{mode}_{timeframe}"),
        InlineKeyboardButton("🧠 Guess", callback_data=f"t_cat_guesser_{mode}_{timeframe}"),
        InlineKeyboardButton("🎴 Char", callback_data=f"t_cat_chars_{mode}_{timeframe}")
    ]]
    if category in ["chars", "guesser"]:
        btns.append([
            InlineKeyboardButton("🕒 Week", callback_data=f"t_cat_{category}_{mode}_weekly"),
            InlineKeyboardButton("🗓 Month", callback_data=f"t_cat_{category}_{mode}_monthly"),
            InlineKeyboardButton("♾ All", callback_data=f"t_cat_{category}_{mode}_all")
        ])
    toggle_text = "🌍 Gʟᴏʙᴀʟ" if mode == "group" else "👥 Gʀᴏᴜᴘ"
    btns.append([InlineKeyboardButton(toggle_text, callback_data=f"t_mode_{category}_{'global' if mode == 'group' else 'group'}_{timeframe}")])
    return InlineKeyboardMarkup(btns)

# --- ⌨️ HANDLERS ---
@Client.on_message(filters.command(["top", "leaderboard"]))
async def top_cmd(client, message):
    # Sends a loading status first since gathering names takes a moment
    status = await message.reply_text("<code>📊 Processing Leaderboard...</code>")
    text = await get_top_text(client, "chars", message.from_user.id)
    await status.edit_text(text, reply_markup=get_top_buttons("chars"), disable_web_page_preview=True)

@Client.on_callback_query(filters.regex(r"^t_"))
async def top_callback(client, query):
    try:
        # Expected pattern: t_cat_CATEGORY_MODE_TIMEFRAME
        parts = query.data.split("_")
        cat, mode, tf = parts[2], parts[3], parts[4]
        c_id = query.message.chat.id if mode == "group" else None
        
        text = await get_top_text(client, cat, query.from_user.id, c_id, tf)
        await query.message.edit_text(text, reply_markup=get_top_buttons(cat, mode, tf), disable_web_page_preview=True)
    except Exception as e:
        print(f"Top Callback Error: {e}")
    finally:
        await query.answer()