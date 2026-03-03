import datetime
import re
import html
import random
import asyncio # Required for sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from database import users, characters, claims, get_disabled_claims

# --- CONFIGURATION ---
SUPPORT_CHAT_ID = -1003375783400 
SUPPORT_LINK = "https://t.me/Tomioka_Supportcore"

RARITY_MAP = {
    "Common": "Common ⚪️", "Legendary": "Legendary 💮", "Rare": "Rare 🍁",
    "Special": "Special 🫧", "Limited": "Limited 🔮", "Celestial": "Celestial 🎐",
    "Manga": "Manga 🔖", "Expensive": "Expensive 💸", "Giveaway": "Demonic ☠",
    "Royal": "Royal 👑", "Summer": "Summer 🏝️", "Winter": "Winter ❄️",
    "Valentine": "Valentine 💝", "Seasonal": "Seasonal 🍂", "Halloween": "🎃",
    "Christmas": "🎄", "AMV": "AMV 🎥"
}

@Client.on_message(filters.command("claim"))
async def claim_waifu(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    today = str(datetime.date.today())

    # 1. Group Restriction Check with Auto-Delete
    if chat_id != SUPPORT_CHAT_ID:
        warn = await message.reply_text(
            "⚠️ <b>Access Denied!</b>\n\n"
            "Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ɪɴ ᴏᴜʀ <b>Sᴜᴘᴘᴏʀᴛ Cʜᴀᴛ</b>. "
            "Jᴏɪɴ ɴᴏᴡ ᴛᴏ ᴄʟᴀɪᴍ ʏᴏᴜʀ ᴅᴀɪʟʏ ᴡᴀɪғᴜ!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Jᴏɪɴ Sᴜᴘᴘᴏʀᴛ Cʜᴀᴛ", url=SUPPORT_LINK)]
            ])
        )
        await asyncio.sleep(30) # Wait for 30 seconds
        try:
            await warn.delete()
            await message.delete() # Delete user's command too
        except:
            pass
        return

    # 2. Fetch User and Check Strict 1-Day Limit
    user = await users.find_one({"$or": [{"_id": user_id}, {"user_id": user_id}]}) or {}
    last_claim_date = user.get("last_claim", "")
    
    if last_claim_date == today:
        return await message.reply_text("⚠️ <b>Yᴏᴜ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ!</b>\nCᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ.")

    # 3. Fetch Disabled Rarities
    disabled_rarities = await get_disabled_claims()
    
    # 4. Build Query
    match_filter = {}
    if disabled_rarities:
        regex_list = [re.compile(f"^{re.escape(r)}", re.IGNORECASE) for r in disabled_rarities]
        match_filter["rarity"] = {"$nin": regex_list}
    
    query = [
        {"$match": match_filter},
        {"$sample": {"size": 1}}
    ]
    
    char_list = await characters.aggregate(query).to_list(1)
    
    if not char_list:
        return await message.reply_text("❌ Nᴏ Wᴀɪғᴜs Aᴠᴀɪʟᴀʙʟᴇ!")
    
    char = char_list[0]

    # 5. Update Database
    await users.update_one(
        {"$or": [{"_id": user_id}, {"user_id": user_id}]}, 
        {"$set": {"last_claim": today}}, 
        upsert=True
    )
    
    await claims.insert_one({
        "user_id": user_id, 
        "char_id": char['id'], 
        "name": char['name'],
        "rarity": char['rarity'], 
        "date": datetime.datetime.now()
    })

    # 6. UI Display
    clean_db_rarity = str(char['rarity']).split(" ")[0].strip()
    display_rarity = RARITY_MAP.get(clean_db_rarity, char['rarity'])

    caption = (
        f"🌊 <b>{html.escape(message.from_user.first_name)}</b>, Yᴏᴜ ᴄʟᴀɪᴍᴇᴅ:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌸 <b>Iᴅ:</b> <code>{char['id']}</code>\n"
        f"💫 <b>Nᴀᴍᴇ:</b> {char['name']}\n"
        f"🌈 <b>Rᴀʀɪᴛʏ:</b> {display_rarity}\n"
        f"🍜 <b>Aɴɪᴍᴇ:</b> {char.get('anime') or char.get('animee', 'Unknown')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎫 <b>Nᴇxᴛ Cʟᴀɪᴍ:</b> ᴛᴏᴍᴏʀʀᴏᴡ"
    )

    file_id = char.get("file_id") or char.get("img_url") or char.get("image")
    
    try:
        await message.reply_photo(photo=file_id, caption=caption)
    except Exception:
        await message.reply_text(caption)