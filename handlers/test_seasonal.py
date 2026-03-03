# Create handlers/test_seasonal.py
from pyrogram import Client, filters
from database import characters, db

@Client.on_message(filters.command("debug_seasonal"))
async def debug_seasonal(client, message):
    # 1. Check characters
    count = await characters.count_documents({"rarity": "Seasonal"})
    
    # 2. Check settings
    config = await db.settings.find_one({"type": "allowed_rarities"})
    allowed = config.get("list", []) if config else []
    is_toggled = "10" in allowed
    
    # 3. Check price
    price_cfg = await db.settings.find_one({"type": "rarity_config", "rarity_id": "10"})
    
    await message.reply_text(
        f"🔍 **Seasonal Diagnostic**\n\n"
        f"📦 Characters in DB: `{count}`\n"
        f"✅ Toggled in Shop: `{is_toggled}` (ID 10)\n"
        f"💰 Price Config: `{price_cfg}`"
    )