from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from collections import defaultdict
import math
import html
from database import characters, claims, users

ITEMS_PER_PAGE = 5

async def build_harem_text(user_id, first_name, last_name, page):
    # 1. Fetch User Preferences (Filter & Favorite)
    user_data = await users.find_one({"_id": user_id}) or {}
    filter_mode = user_data.get("harem_mode", "all")
    fav_id = user_data.get("fav_id")

    # 2. Build DB Query
    query = {"user_id": user_id}
    if filter_mode != "all":
        query["rarity"] = filter_mode

    user_claims = await claims.find(query).to_list(length=None)
    total_waifus = len(user_claims)
    full_name = html.escape(f"{first_name} {last_name}" if last_name else first_name)

    if total_waifus == 0:
        filter_text = f" in <b>{filter_mode}</b>" if filter_mode != "all" else ""
        return f"👤 <b>Oᴡɴᴇʀ:</b> {full_name}\n\n💔 Yᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ{filter_text} ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴇᴍᴘᴛʏ.", 0, 0

    # 3. Get Character details & group them
    char_ids = [c['char_id'] for c in user_claims]
    full_chars = await characters.find({"id": {"$in": char_ids}}).to_list(length=None)

    char_counts = defaultdict(int)
    for c in user_claims:
        char_counts[c['char_id']] += 1
        
    anime_map = defaultdict(list)
    unique_chars = {char['id']: char for char in full_chars}
    for char_id, char in unique_chars.items():
        anime_map[char["anime"]].append(char)

    anime_list = sorted(anime_map.items())
    total_pages = math.ceil(len(anime_list) / ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    # --- TEXT HEADER ---
    mode_label = f" ({filter_mode.upper()})" if filter_mode != "all" else ""
    text = f"🌸 <b>Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ Cᴏʟʟᴇᴄᴛɪᴏɴ{mode_label}</b> 🌸\n"
    text += f"👤 <b>Oᴡɴᴇʀ:</b> {full_name}\n"
    text += f"✨ <b>Tᴏᴛᴀʟ Wᴀɪғᴜs:</b> <code>{total_waifus}</code>\n\n"

    for anime, chars in anime_list[start:end]:
        text += f"╭ 『 <b>{html.escape(anime)}</b> 』\n"
        for c in chars:
            count = char_counts[c['id']]
            count_text = f" x{count}" if count > 1 else ""
            # Use ⭐ if it's the favorite, otherwise ✦
            mark = "⭐" if c['id'] == fav_id else "✦"
            text += f"│ {mark} <code>{c['id']}</code> <b>{html.escape(c['name'])}</b>{count_text}\n"
        text += "╰──────────────\n\n"

    return text, total_pages, total_waifus

@Client.on_message(filters.command("harem"))
async def harem(client, message):
    user = message.from_user
    text, pages, total = await build_harem_text(user.id, user.first_name, user.last_name, 1)
    
    buttons = []
    if pages > 1:
        buttons.append([
            InlineKeyboardButton("⏪", callback_data="harem_1"),
            InlineKeyboardButton("◀️", callback_data="harem_1"),
            InlineKeyboardButton(f"1/{pages}", callback_data="noop"),
            InlineKeyboardButton("▶️", callback_data="harem_2"),
            InlineKeyboardButton("⏩", callback_data=f"harem_{pages}")
        ])
    
    buttons.append([
        InlineKeyboardButton("⚙️ Fɪʟᴛᴇʀ", callback_data="wmode_back"),
        InlineKeyboardButton("🌐 Sᴇᴀʀᴄʜ", switch_inline_query_current_chat="")
    ])

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^harem_(\d+)"))
async def harem_callback(client, query):
    page = int(query.data.split("_")[1])
    user = query.from_user
    text, pages, total = await build_harem_text(user.id, user.first_name, user.last_name, page)
    
    buttons = []
    if pages > 1:
        buttons.append([
            InlineKeyboardButton("⏪", callback_data="harem_1"),
            InlineKeyboardButton("◀️", callback_data=f"harem_{page-1 if page > 1 else 1}"),
            InlineKeyboardButton(f"{page}/{pages}", callback_data="noop"),
            InlineKeyboardButton("▶️", callback_data=f"harem_{page+1 if page < pages else pages}"),
            InlineKeyboardButton("⏩", callback_data=f"harem_{pages}")
        ])
    
    buttons.append([
        InlineKeyboardButton("⚙️ Fɪʟᴛᴇʀ", callback_data="wmode_back"),
        InlineKeyboardButton("🌐 Sᴇᴀʀᴄʜ", switch_inline_query_current_chat="")
    ])

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)