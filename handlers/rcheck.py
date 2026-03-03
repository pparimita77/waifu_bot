from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import characters, staff
from config import OWNER_ID, DEVS

# Updated Rarity Display Map with all 17 Rarities
RARITY_MAP = {
    "Common": "Common ⚪️", 
    "Legendary": "Legendary 💮", 
    "Rare": "Rare 🍁",
    "Special": "Special 🫧", 
    "Limited": "Limited 🔮", 
    "Celestial": "Celestial 🎐",
    "Manga": "Manga 🔖", 
    "Expensive": "Expensive 💸", 
    "Demonic": "Demonic ☠",
    "Royal": "Royal 👑", 
    "Summer": "Summer 🏝️", 
    "Winter": "Winter ❄️",
    "Valentine": "Valentine 💝", 
    "Seasonal": "Seasonal 🍂", 
    "Halloween": "Halloween 🎃",
    "Christmas": "Christmas 🎄", 
    "AMV": "AMV 🎥"
}

@Client.on_message(filters.command("rcheck"))
async def rarity_stats_cmd(client, message):
    user_id = message.from_user.id
    
    # --- 1. AUTHORIZATION CHECK ---
    user_staff = await staff.find_one({"_id": user_id})
    is_staff = user_staff and user_staff.get("role") in ["sudo", "dev", "uploader"]
    is_admin = user_id == OWNER_ID or user_id in (DEVS or [])

    if not is_admin and not is_staff:
        return await message.reply_text("🚫 **Access Denied!** This command is for Staff only.")

    # --- 2. DATA PROCESSING ---
    sent_msg = await message.reply_text("📊 **Calculating Rarity Statistics...**")

    # Group characters by rarity and count them
    pipeline = [
        {"$group": {"_id": "$rarity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}} # Highest count first
    ]
    
    results = await characters.aggregate(pipeline).to_list(None)
    
    if not results:
        return await sent_msg.edit_text("❌ **No characters found in the database.**")

    total_characters = sum(item['count'] for item in results)
    
    # --- 3. UI CONSTRUCTION ---
    stats_text = "📊 **Gʟᴏʙᴀʟ Rᴀʀɪᴛʏ Sᴛᴀᴛɪsᴛɪᴄs**\n"
    stats_text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for entry in results:
        db_rarity = entry['_id']
        count = entry['count']
        
        # Clean the rarity name to handle strings like "Common ⚪️" or just "Common"
        clean_rarity = str(db_rarity).split(" ")[0].strip()
        display_name = RARITY_MAP.get(clean_rarity, db_rarity)
        
        # Calculation for percentage
        percentage = (count / total_characters) * 100
        stats_text += f"<b>{display_name}</b>\n└ Count: <code>{count}</code> ({percentage:.1f}%)\n\n"

    stats_text += "━━━━━━━━━━━━━━━━━━━━\n"
    stats_text += f"Total Characters Uploaded: <b>{total_characters}</b>"

    await sent_msg.edit_text(stats_text, parse_mode=ParseMode.HTML)