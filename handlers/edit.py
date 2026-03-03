import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import characters

# --- CONFIGURATION ---
DEV_USERS = [8325139144, 7987799736] # Add other Dev IDs here

# Mapping numbers to Rarity Names
RARITY_MAP = {
    "1": "Common", "2": "Legendary", "3": "Rare", 
    "4": "Special", "5": "Limited", "6": "Celestial",
    "7": "Manga", "8": "Expensive", "9": "Demonic", 
    "10": "Royal", "11": "Summer", "12": "Winter",
    "13": "Valentine", "14": "Seasonal", "15": "Halloween",
    "16": "Christmas", "17": "AMV"
}

@Client.on_message(filters.command("edit") & filters.user(DEV_USERS))
async def edit_character(client, message):
    # We use maxsplit=2 to allow names with spaces
    # Format: /edit ID RarityNum Name
    args = message.text.split(maxsplit=3)
    
    if len(args) < 4:
        return await message.reply_text(
            "<b>Format:</b> `/edit <id> <rarity_num> <new_name>`\n"
            "<b>Example:</b> `/edit 01 2 Naruto Uzumaki` (Sets ID 01 to Legendary & Name to Naruto Uzumaki)"
        )

    char_id = args[1]
    rarity_num = args[2]
    new_name = args[3]

    # Check if the number provided is valid
    if rarity_num not in RARITY_MAP:
        return await message.reply_text("❌ Invalid Rarity Number (Use 1-17).")
    
    new_rarity = RARITY_MAP[rarity_num]

    # 1. Check if character exists
    char = await characters.find_one({"id": char_id})
    if not char:
        return await message.reply_text(f"❌ Character ID <code>{char_id}</code> not found.")

    # 2. Update Database
    await characters.update_one(
        {"id": char_id},
        {"$set": {
            "name": new_name,
            "rarity": new_rarity
        }}
    )

    # 3. Success Message
    response = (
        f"✅ <b>Character Updated Successfully!</b>\n\n"
        f"🆔 <b>ID:</b> <code>{char_id}</code>\n"
        f"👤 <b>New Name:</b> <code>{new_name}</code>\n"
        f"✨ <b>New Rarity:</b> <code>{new_rarity}</code>"
    )

    await message.reply_text(response, parse_mode=ParseMode.HTML)