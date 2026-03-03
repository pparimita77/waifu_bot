from pyrogram import Client, filters
from database import db
from config import OWNER_ID  # Using OWNER_ID for "Only by Owner" access
from .setcost import RARITY_MAP # Import the map from your setcost file

settings = db.settings

@Client.on_message(filters.command(["shopcosts", "costs"]))
async def view_shop_costs(client, message):
    # Strict Owner Only check
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **This command is reserved for the Bot Owner.**")

    text = "💰 **Cᴜʀʀᴇɴᴛ Rᴀʀɪᴛʏ Pʀɪᴄɪɴɢ**\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "ID | Rarity | Price Range (💎)\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"

    # Fetch all configurations from database
    all_configs = await settings.find({"type": "rarity_config"}).to_list(length=20)
    # Convert list to dictionary for quick lookup: { "1": {"min": 10, "max": 20}, ... }
    price_data = {item['rarity_id']: item for item in all_configs}

    for r_id in sorted(RARITY_MAP.keys(), key=int):
        r_name, r_emoji = RARITY_MAP[r_id]
        
        if r_id in price_data:
            min_p = price_data[r_id].get("min_price", 0)
            max_p = price_data[r_id].get("max_price", 0)
            price_text = f"**{min_p:,} - {max_p:,}**"
        else:
            price_text = "Not Set ❌"

        text += f"`{r_id.ljust(2)}` | {r_emoji} {r_name.ljust(10)} | {price_text}\n"

    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "📝 Use `/setcost <ID> <min> <max>` to update."

    await message.reply_text(text)