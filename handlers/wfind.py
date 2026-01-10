from pyrogram import Client, filters
from database import characters

@Client.on_message(filters.command("wfind"))
async def wfind_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("📝 **Usage:** `/wfind <name or id>`")

    query_input = " ".join(message.command[1:]).strip()
    
    # 1. Try to find by ID first
    # We check both string and integer versions of the ID to be safe
    char = await characters.find_one({
        "$or": [
            {"id": query_input},
            {"id": int(query_input) if query_input.isdigit() else None}
        ]
    })

    # 2. If not found by ID, try searching by Name (Case-Insensitive)
    if not char:
        char = await characters.find_one({"name": {"$regex": f"^{query_input}$", "$options": "i"}})

    if not char:
        return await message.reply_text(f"❌ No character found with ID or Name: **{query_input}**")

    # Rarity Emoji Map
    RARITY_EMOJI = {
        "Common": "⚪", "Rare": "🏵️", "Special": "🫧", "Legendary": "💮",
        "Limited": "🔮", "Celestial": "🎐", "Manga": "🔖", "Expensive": "💸",
        "Giveaway": "🧧", "Seasonal": "🍂", "Valentine": "💝", "AMV": "🎥"
    }
    emoji = RARITY_EMOJI.get(char.get("rarity"), "✨")

    caption = (
        f"🔍 **Cʜᴀʀᴀᴄᴛᴇʀ Fᴏᴜɴᴅ!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{char['id']}`\n"
        f"👤 **Nᴀᴍᴇ:** {char['name']}\n"
        f"🍜 **Aɴɪᴍᴇ:** {char['anime']}\n"
        f"{emoji} **Rᴀʀɪᴛʏ:** {char['rarity']}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await message.reply_photo(photo=char['file_id'], caption=caption)
    except Exception as e:
        await message.reply_text(f"❌ Error displaying image: {e}")