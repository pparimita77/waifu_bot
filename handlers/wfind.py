from pyrogram import Client, filters
from database import characters, claims, users # Ensure users collection is imported for names
from pyrogram.types import Message

@Client.on_message(filters.command("wfind") & filters.group, group=0)
async def wfind_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🔍 **Usage:** `/wfind <ID, Name, or Rarity>`")

    query = message.text.split(" ", 1)[1].strip()

    # 1. Search for Character
    search_filter = {
        "$or": [
            {"id": query},
            {"id": int(query) if query.isdigit() else None},
            {"name": {"$regex": query, "$options": "i"}},
            {"anime": {"$regex": query, "$options": "i"}},
            {"rarity": {"$regex": query, "$options": "i"}}
        ]
    }
    # Clean the filter
    search_filter["$or"] = [x for x in search_filter["$or"] if x.get("id") is not None or any(k in x for k in ["name", "anime", "rarity"])]

    char = await characters.find_one(search_filter)

    if not char:
        return await message.reply_text(f"❌ No character found matching: `{query}`")

    char_id = char['id']

    # 2. Fetch Top 10 Grabbers
    # We find all claims for this char_id, group by user, and sort by date or count
    # For a simple 'Top Grabbers' list (first 10 people to claim it):
    grabbers_cursor = claims.find({"char_id": char_id}).sort("date", 1).limit(10)
    grabbers_list = []
    
    counter = 1
    async for claim in grabbers_cursor:
        try:
            user = await client.get_users(claim['user_id'])
            user_name = user.first_name
            grabbers_list.append(f"{counter}. [{user_name}](tg://user?id={claim['user_id']})")
            counter += 1
        except:
            grabbers_list.append(f"{counter}. Unknown User")
            counter += 1

    grabbers_text = "\n".join(grabbers_list) if grabbers_list else "No grabbers yet."

    # 3. Format Response
    caption = (
        f"🔍 **Cʜᴀʀᴀᴄᴛᴇʀ Dᴇᴛᴀɪʟs**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{char.get('id')}`\n"
        f"👤 **Nᴀᴍᴇ:** {char.get('name')}\n"
        f"🎌 **Aɴɪᴍᴇ:** {char.get('anime')}\n"
        f"✨ **Rᴀʀɪᴛʏ:** {char.get('rarity', 'Common ⚪️')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 **Tᴏᴘ 10 Gʀᴀʙʙᴇʀs:**\n"
        f"{grabbers_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    # 4. Send Result
    try:
        photo = char.get('file_id')
        if photo:
            await message.reply_photo(photo=photo, caption=caption)
        else:
            await message.reply_text(caption)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")