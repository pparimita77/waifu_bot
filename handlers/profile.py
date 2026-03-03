from pyrogram import Client, filters
import html
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from database import users, claims, characters, is_user_premium

# --- CONFIGURATION ---
AUTH_CHANNEL = "Tomioka_Supportcore"

# RANK CONFIGURATION
RANKS = [
    (0, "Mizunoto", "🌊"),
    (500, "Mizunoe", "💧"),
    (1500, "Kanoto", "🌫️"),
    (3000, "Kanoe", "🎋"),
    (6000, "Tsuchinoto", "🪵"),
    (10000, "Tsuchinoe", "🌿"),
    (15000, "Hinoto", "🔥"),
    (25000, "Hinoe", "☀️"),
    (40000, "Kinoto", "⚡"),
    (70000, "Hashira", "💎")
]

# --- HELPERS ---
async def is_subscribed(client, user_id):
    try:
        await client.get_chat_member(AUTH_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True

def get_rank_info(exp_score):
    current = RANKS[0]
    next_req = "MAX"
    for i, r in enumerate(RANKS):
        if exp_score >= r[0]:
            current = r
            if i + 1 < len(RANKS):
                next_req = RANKS[i+1][0]
        else:
            break
    
    if next_req != "MAX":
        total_needed = next_req - current[0]
        current_progress = exp_score - current[0]
        percent = max(0, min(10, int((current_progress / total_needed) * 10)))
        bar = "🔹" * percent + "▫️" * (10 - percent)
        progress_text = f"{exp_score:,}/{next_req:,}\n<code>{bar}</code>"
    else:
        progress_text = f"{exp_score:,} (🏆 Mᴀx Rᴀɴᴋ)"
        
    return current, progress_text

# --- PROFILE COMMAND ---
@Client.on_message(filters.command("profile"))
async def profile_cmd(client, message):
    user = message.from_user
    user_id = user.id
    
    if not await is_subscribed(client, user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Jᴏɪɴ Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{AUTH_CHANNEL}")],
            [InlineKeyboardButton("🔄 Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{client.me.username}?start=check")]
        ])
        return await message.reply_text("❌ <b>Join our support group to view your profile!</b>", reply_markup=buttons)

    data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]}) or {}
    
    emeralds = float(data.get("emeralds", 0))
    stardust = float(data.get("stardust", 0))
    user_exp = data.get("exp") or data.get("xp") or 0
    fav_id = str(data.get("favorite", ""))
    
    global_rank = await users.count_documents({"emeralds": {"$gt": emeralds}}) + 1
    total_claims = await claims.count_documents({"user_id": user_id})
    
    (thresh, rank_name, rank_emoji), progress_display = get_rank_info(user_exp)
    
    is_premium = await is_user_premium(user_id)
    premium_tag = " 👑 [ᴘʀᴇᴍɪᴜᴍ]" if is_premium else ""
    premium_footer = "\n✨ <i>ᴘʀᴇᴍɪᴜᴍ ᴘᴇʀᴋs ᴀᴄᴛɪᴠᴇ</i>" if is_premium else ""

    media_to_show = None
    is_video = False
    fav_text = "Nᴏɴᴇ Sᴇᴛ"
    
    # Check Favorite first
    if fav_id and fav_id not in ["", "None"]:
        char = await characters.find_one({"id": fav_id})
        if char:
            fav_text = f"{char['name']} ({char['anime']})"
            media_to_show = char.get('file_id') or char.get('image')
            is_video = "amv" in char.get('rarity', '').lower() or char.get("is_video", False)

    # Fallback to last claim
    if not media_to_show:
        last_claim = await claims.find_one({"user_id": user_id}, sort=[("_id", -1)])
        if last_claim:
            last_char = await characters.find_one({"id": last_claim.get('char_id')})
            if last_char:
                media_to_show = last_char.get('file_id') or last_char.get('image')
                is_video = "amv" in last_char.get('rarity', '').lower() or last_char.get("is_video", False)

    caption = (
        f"🌊 <b>ᴛᴏᴍɪᴏᴋᴀ ɢɪʏᴜ ʜᴜɴᴛᴇʀ ᴘʀᴏꜰɪʟᴇ</b>{premium_tag}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Nᴀᴍᴇ:</b> {html.escape(user.first_name)}\n"
        f"🏆 <b>Gʟᴏʙᴀʟ Rᴀɴᴋ:</b> <code>#{global_rank}</code>\n"
        f"🎖️ <b>Rᴀɴᴋ:</b> {rank_emoji} {rank_name}\n"
        f"📈 <b>EXP:</b> {progress_display}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💠 <b>Eᴍᴇʀᴀʟᴅs:</b> <code>{emeralds:,.2f}</code>\n"
        f"🌟 <b>Sᴛᴀʀᴅᴜsᴛ:</b> <code>{stardust:,.2f}</code>\n"
        f"🎴 <b>Hᴀʀᴇᴍ:</b> <code>{total_claims}</code> chars\n"
        f"🌸 <b>Fᴀᴠᴏʀɪᴛᴇ:</b> {html.escape(fav_text)}\n"
        f"━━━━━━━━━━━━━━━━━━━━{premium_footer}"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌸 Cʜᴀɴɢᴇ Fᴀᴠᴏʀɪᴛᴇ", callback_data=f"set_fav_prompt_{user_id}")],
        [InlineKeyboardButton("🎴 Vɪᴇᴡ Hᴀʀᴇᴍ", switch_inline_query_current_chat=f"harem {user_id}")]
    ])

    try:
        if media_to_show:
            if is_video:
                await message.reply_video(video=media_to_show, caption=caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
            else:
                await message.reply_photo(photo=media_to_show, caption=caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)

# --- CALLBACKS & FAV COMMAND ---
@Client.on_callback_query(filters.regex(r"^set_fav_prompt_"))
async def fav_prompt(client, query: CallbackQuery):
    user_id = int(query.data.split("_")[-1])
    if query.from_user.id != user_id:
        return await query.answer("🚫 Not your profile!", show_alert=True)
    
    await query.answer()
    await query.message.reply_text("🌸 Send <code>/fav ID</code> to set your favorite character!")

@Client.on_message(filters.command("fav"))
async def set_favorite_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/fav [Character ID]`")
    
    char_id = message.command[1]
    user_id = message.from_user.id
    
    own = await claims.find_one({"user_id": user_id, "$or": [{"char_id": char_id}, {"id": char_id}]})
    if not own:
        return await message.reply_text("❌ Yᴏᴜ ᴅᴏɴ'ᴛ ᴏᴡɴ ᴛʜɪs ᴄʜᴀʀᴀᴄᴛᴇʀ!")

    await users.update_one({"$or": [{"user_id": user_id}, {"_id": user_id}]}, {"$set": {"favorite": char_id}})
    await message.reply_text("✅ Favorite updated!")