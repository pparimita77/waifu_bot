from pyrogram import Client, filters
from database import characters

@Client.on_message(filters.command("wfind") & filters.group, group=0)
async def wfind_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🔍 **Usage:** `/wfind <ID or Name>`")

    query = message.text.split(" ", 1)[1].strip()
    
    # 1. Try to find by ID (checking both string and int)
    char = await characters.find_one({
        "$or": [
            {"id": query},
            {"id": int(query) if query.isdigit() else None},
            {"name": {"$regex": f"^{query}$", "$options": "i"}} # Case-insensitive name match
        ]
    })

    if not char:
        return await message.reply_text(f"❌ No character found for: `{query}`")

    # 2. Success Response
    caption = (
        f"🔍 **Character Found!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{char['id']}`\n"
        f"👤 **Name:** {char['name']}\n"
        f"🎌 **Anime:** {char['anime']}\n"
        f"✨ **Rarity:** {char['rarity']}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await message.reply_photo(photo=char['file_id'], caption=caption)
    except Exception:
        await message.reply_text(caption)