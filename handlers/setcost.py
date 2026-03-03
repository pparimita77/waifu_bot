from pyrogram import Client, filters
from database import db
from config import OWNER_ID, DEVS # Ensuring it checks for proper dev access

# Matches the Shop mapping exactly
RARITY_MAP = {
    "1": ("Common", "⚪️"), "2": ("Legendary", "💮"), "3": ("Rare", "🍁"),
    "4": ("Special", "🫧"), "5": ("Limited", "🔮"), "6": ("Celestial", "🎐"),
    "7": ("Manga", "🔖"), "8": ("Expensive", "💸"), "9": ("Demonic", "☠"),
    "10": ("Royal", "👑"), "11": ("Summer", "🏝️"), "12": ("Winter", "❄️"),
    "13": ("Valentine", "💝"), "14": ("Seasonal", "🍂"), "15": ("Halloween", "🎃"),
    "16": ("Christmas", "🎄"), "17": ("AMV", "🎥")
}

settings = db.settings

@Client.on_message(filters.command("setcost"))
async def set_shop_cost(client, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID and user_id not in (DEVS or []):
        return await message.reply_text("🚫 **Dev Access Only.**")

    if len(message.command) < 4:
        return await message.reply_text(
            "📝 **Usage:** `/setcost <rarity_no> <min> <max>`\n"
            "💡 **Example:** `/setcost 2 500 1000` (Sets Legendary cost)"
        )

    try:
        r_id = message.command[1]
        min_p = int(message.command[2])
        max_p = int(message.command[3])

        if r_id not in RARITY_MAP:
            return await message.reply_text("❌ **Invalid Rarity!** Use numbers **1-17**.")

        if min_p > max_p:
            return await message.reply_text("❌ **Min price** cannot be higher than **Max price**.")

        # Updated field names to match the Shop's logic (min/max)
        await settings.update_one(
            {"type": "rarity_config", "rarity_id": r_id},
            {"$set": {"min": min_p, "max": max_p}}, 
            upsert=True
        )
        
        # Trigger an immediate shop refresh so the new costs apply now
        await settings.delete_one({"type": "daily_shop"})
        
        r_name, r_emoji = RARITY_MAP[r_id]
        await message.reply_text(
            f"✅ **{r_emoji} {r_name}** cost updated!\n"
            f"💰 **Range:** `{min_p:,}` - `{max_p:,}` 💠 Emeralds\n\n"
            f"♻️ *Shop cache cleared. Next /shop will use these prices.*"
        )
        
    except ValueError:
        await message.reply_text("❌ Prices must be numeric values.")