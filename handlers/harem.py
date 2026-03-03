import math
import html
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQueryResultArticle, 
    InlineQueryResultCachedPhoto, 
    InlineQueryResultCachedVideo,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
    InputTextMessageContent,
    CallbackQuery 
)
from database import characters, claims, users

# --- CONFIGURATION ---
DEFAULT_THUMB = "https://telegra.ph/file/0c35695f36e9d6d34b611.jpg" 
ITEMS_PER_PAGE = 10 

RARITY_SYMBOLS = {
    "Common": "⚪️", "Legendary": "💮", "Rare": "🍁", 
    "Special": "🫧", "Limited": "🔮", "Celestial": "🎐",
    "Manga": "🔖", "Expensive": "💸", "Demonic": "☠", 
    "Royal": "👑", "Summer": "🏝️", "Winter": "❄️",
    "Valentine": "💝", "Seasonal": "🍂", "Halloween": "🎃",
    "Christmas": "🎄", "AMV": "🎥"
}

# --- TEXT BUILDER (OBEYS CMODE) ---
async def build_harem_text(user_id, first_name, last_name, page):
    # Fetch user preferences for cmode
    user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]}) or {}
    fav_id = str(user_data.get("favorite", "")) 
    harem_mode = user_data.get("harem_mode", "all")

    user_claims = await claims.find({"user_id": user_id}).to_list(length=None)
    if not user_claims:
        return "💔 Your collection is empty.", 0, 0, None, False

    char_ids = [c['char_id'] for c in user_claims]
    
    # Build Character Filter based on cmode
    char_filter = {"id": {"$in": char_ids}}
    if harem_mode != "all":
        char_filter["rarity"] = {"$regex": f"^{harem_mode}", "$options": "i"}

    all_matching_chars = await characters.find(char_filter).to_list(length=None)
    
    if not all_matching_chars:
        if harem_mode != "all":
            return f"❌ You don't have any **{harem_mode.capitalize()}** characters yet.", 0, 0, None, False
        return "💔 Your collection is empty.", 0, 0, None, False

    total_chars = len(all_matching_chars)
    total_pages = math.ceil(total_chars / ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * ITEMS_PER_PAGE
    page_chars = all_matching_chars[start:start + ITEMS_PER_PAGE]

    fav_image, fav_name, fav_is_video = None, "None Set", False
    # Check all owned chars for the favorite one
    for char in all_matching_chars:
        if str(char['id']) == fav_id:
            fav_name = html.escape(char.get('name', 'Unknown'))
            fav_image = char.get('file_id') or char.get('image')
            fav_is_video = "amv" in char.get('rarity', '').lower()

    mode_label = f" ({harem_mode.capitalize()})" if harem_mode != "all" else ""
    text = (
        f"🌸 <b>{first_name}'s Collection{mode_label}</b> 🌸\n"
        f"⭐️ <b>Favorite:</b> {fav_name}\n"
        f"✨ <b>Total Waifus:</b> <code>{total_chars}</code>\n\n"
    )

    for char in page_chars:
        raw_rarity = str(char.get('rarity', 'Common')).split()[0].capitalize()
        symbol = RARITY_SYMBOLS.get(raw_rarity, "⚪️")
        text += f"╭〔 <b>{html.escape(char.get('anime', 'Unknown'))}</b> 〕\n│ ✦ {char.get('id')} | {symbol} | <b>{html.escape(char.get('name', 'Unknown'))}</b>\n╰──────────────\n\n"

    return text, total_pages, total_chars, fav_image, fav_is_video

# --- CALLBACK HANDLER ---
@Client.on_callback_query(filters.regex(r"^hr_(\d+)_(\d+)$"))
async def harem_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.matches[0].group(1))
    target_page = int(callback_query.matches[0].group(2))
    
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("This is not your harem!", show_alert=True)

    text, pages, total, fav_img, is_vid = await build_harem_text(
        user_id, callback_query.from_user.first_name, callback_query.from_user.last_name, target_page
    )

    kb = [[InlineKeyboardButton("🔥 Collection", switch_inline_query_current_chat=f"harem {user_id}")]]
    if pages > 1:
        prev_p = pages if target_page == 1 else target_page - 1
        next_p = 1 if target_page == pages else target_page + 1
        kb.insert(0, [
            InlineKeyboardButton("◀️", callback_data=f"hr_{user_id}_{prev_p}"),
            InlineKeyboardButton(f"{target_page}/{pages}", callback_data="noop"),
            InlineKeyboardButton("▶️", callback_data=f"hr_{user_id}_{next_p}")
        ])

    try:
        await callback_query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb))
    except Exception:
        # Fallback if the message is only text
        await callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(kb))

# --- COMMAND HANDLER ---
@Client.on_message(filters.command("harem"))
async def harem_cmd(client, message):
    user = message.from_user
    text, pages, total, fav_img, is_vid = await build_harem_text(user.id, user.first_name, user.last_name, 1)
    
    kb = [[InlineKeyboardButton("🔥 Collection", switch_inline_query_current_chat=f"harem {user.id}")]]
    if pages > 1:
        kb.insert(0, [
            InlineKeyboardButton("◀️", callback_data=f"hr_{user.id}_{pages}"),
            InlineKeyboardButton(f"1/{pages}", callback_data="noop"),
            InlineKeyboardButton("▶️", callback_data=f"hr_{user.id}_2")
        ])

    reply_markup = InlineKeyboardMarkup(kb)
    if fav_img:
        if is_vid: await message.reply_video(fav_img, caption=text, reply_markup=reply_markup)
        else: await message.reply_photo(fav_img, caption=text, reply_markup=reply_markup)
    else:
        await message.reply_text(text, reply_markup=reply_markup)

# --- INLINE HANDLER ---
@Client.on_inline_query()
async def inline_handler(client, query):
    string = query.query.lower().strip()
    
    # 1. TOP 10 SEARCH
    if string == "top":
        try:
            pipeline = [{"$group": {"_id": "$user_id", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
            top_users = await claims.aggregate(pipeline).to_list(length=10)
            
            leaderboard_text = "🏆 <b>TOP 10 CHARACTER COLLECTORS</b> 🏆\n\n"
            for i, user_entry in enumerate(top_users, 1):
                u_id = user_entry["_id"]
                db_user = await users.find_one({"$or": [{"user_id": u_id}, {"_id": u_id}]})
                
                if db_user and db_user.get("first_name"):
                    name = html.escape(db_user["first_name"])
                else:
                    try:
                        tg_user = await client.get_users(u_id)
                        name = html.escape(tg_user.first_name)
                        await users.update_one({"user_id": u_id}, {"$set": {"first_name": name}}, upsert=True)
                    except:
                        name = f"User {u_id}"

                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "✨"
                leaderboard_text += f"{medal} {i}. <b>{name}</b> — <code>{user_entry['count']}</code> Chars\n"

            results = [InlineQueryResultArticle(
                title="🏆 View Top 10 Grabbers",
                thumb_url=DEFAULT_THUMB,
                input_message_content=InputTextMessageContent(leaderboard_text, parse_mode=ParseMode.HTML)
            )]
            return await query.answer(results=results, cache_time=1)
        except Exception as e:
            print(f"Top Inline Error: {e}")

    # 2. HAREM SEARCH
    if string.startswith("harem"):
        try:
            parts = string.split(maxsplit=2)
            target_id = query.from_user.id
            search_query = ""
            
            if len(parts) > 1:
                if parts[1].isdigit():
                    target_id = int(parts[1])
                    if len(parts) > 2: search_query = parts[2]
                else:
                    search_query = " ".join(parts[1:])

            all_user_claims = await claims.find({"user_id": target_id}).to_list(length=None)
            if not all_user_claims:
                return await query.answer([], switch_pm_text="Harem is empty!", switch_pm_parameter="help")

            char_ids = [c['char_id'] for c in all_user_claims]
            char_filter = {"id": {"$in": char_ids}}
            if search_query:
                char_filter["$or"] = [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"anime": {"$regex": search_query, "$options": "i"}}
                ]

            all_chars = await characters.find(char_filter).to_list(length=50)
            results = []
            for char in all_chars:
                cid, name, anime = char.get("id"), html.escape(char.get("name")), html.escape(char.get("anime"))
                rarity = char.get("rarity", "Common")
                symbol = RARITY_SYMBOLS.get(str(rarity).split()[0].capitalize(), "⚪️")
                media_id = char.get('file_id') or char.get('image')
                is_vid = "amv" in rarity.lower()
                
                caption = (
                    f"✨ <b>OwO! Look at this character!</b> ✨\n\n"
                    f"🌟 <b>Name:</b> {name}\n"
                    f"🎬 <b>Anime:</b> {anime}\n"
                    f"🔮 <b>Rarity:</b> {rarity} {symbol}\n"
                    f"🆔 <b>ID:</b> <code>{cid}</code>\n"
                    f"👥 <b>Total Owned:</b> {len(all_user_claims)} Chars"
                )
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏆 Leaderboard", switch_inline_query_current_chat="top")]])
                
                if str(media_id).startswith(("http", "https")):
                    if is_vid: results.append(InlineQueryResultVideo(video_url=media_id, thumb_url=media_id, title=name, caption=caption, reply_markup=kb))
                    else: results.append(InlineQueryResultPhoto(photo_url=media_id, thumb_url=media_id, title=name, caption=caption, reply_markup=kb))
                else:
                    if is_vid: results.append(InlineQueryResultCachedVideo(video_file_id=media_id, title=name, caption=caption, reply_markup=kb))
                    else: results.append(InlineQueryResultCachedPhoto(photo_file_id=media_id, title=name, caption=caption, reply_markup=kb))
            
            await query.answer(results=results, cache_time=1)
        except Exception as e:
            print(f"Harem Inline Error: {e}")