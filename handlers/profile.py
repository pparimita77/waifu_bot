from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import users, claims, characters
import html

# --- RANK CONFIGURATION (Based on EXP) ---
RANKS = [
    (0, "Rookie", "⚔️"),
    (500, "Mizunoto", "🌊"),
    (1500, "Kanoe", "🎋"),
    (5000, "Hashira", "💎"),
    (15000, "Water Hashira", "🌊🌀"),
    (50000, "Demon King", "👑")
]

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
    progress = f"{exp_score:,}/{next_req:,}" if next_req != "MAX" else "Max Level"
    return current, progress

@Client.on_message(filters.command("profile"))
async def profile_cmd(client, message):
    user = message.from_user
    
    # 1. Fetch User Data
    user_data = await users.find_one({"_id": user.id}) or {}
    balance = user_data.get("balance", 0)
    user_exp = user_data.get("total_exp", 0)
    fav_id = user_data.get("fav_id")
    
    # 2. Fetch Stats
    total_claims = await claims.count_documents({"user_id": user.id})
    (thresh, rank_name, rank_emoji), progress = get_rank_info(user_exp)

    # 3. Image and Favorite Logic
    photo_to_show = None
    fav_text = "None Set"
    
    # Priority: Favorite ID > Last Caught Character
    target_id = fav_id
    if not target_id:
        last_claim = await claims.find_one({"user_id": user.id}, sort=[("_id", -1)])
        if last_claim:
            target_id = last_claim['char_id']

    if target_id:
        char = await characters.find_one({"id": target_id})
        if char:
            fav_text = f"{char['name']} ({char['anime']})"
            photo_to_show = char['file_id']

    # 4. Final Text Construction
    caption = (
        f"🌊 <b>ᴛᴏᴍɪᴏᴋᴀ ɢɪʏᴜ ʜᴜɴᴛᴇʀ ᴘʀᴏꜰɪʟᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Name:</b> {html.escape(user.first_name)}\n"
        f"🎖️ <b>Rank:</b> {rank_emoji} {rank_name}\n"
        f"📈 <b>EXP:</b> <code>{progress}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Coins:</b> <code>{balance:,}</code>\n"
        f"🎴 <b>Harem:</b> <code>{total_claims}</code> chars\n"
        f"🏆 <b>Favorite:</b> {html.escape(fav_text)}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    # 5. Send Result
    try:
        if photo_to_show:
            await message.reply_photo(photo=photo_to_show, caption=caption, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text(caption, parse_mode=ParseMode.HTML)
    except:
        await message.reply_text(caption, parse_mode=ParseMode.HTML)