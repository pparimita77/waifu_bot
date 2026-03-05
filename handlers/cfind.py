import html
from pyrogram import Client, filters
from database import characters, claims
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("cfind") & filters.group, group=0)
async def cfind_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "🔍 <b>Usage:</b> <code>/cfind &lt;ID, Name, or Anime&gt;</code>",
            parse_mode=ParseMode.HTML
        )

    query = message.text.split(" ", 1)[1].strip()

    # Search filter logic
    search_filter = {
        "$or": [
            {"id": query},
            {"id": int(query) if query.isdigit() else None},
            {"name": {"$regex": query, "$options": "i"}},
            {"anime": {"$regex": query, "$options": "i"}}
        ]
    }
    search_filter["$or"] = [x for x in search_filter["$or"] if any(v is not None for v in x.values())]
    
    char = await characters.find_one(search_filter)

    if not char:
        return await message.reply_text(
            f"❌ <b>No character found matching:</b> <code>{html.escape(query)}</code>",
            parse_mode=ParseMode.HTML
        )

    char_id = str(char['id'])

    # Top 10 Grabbers Aggregation Pipeline
    pipeline = [
        {"$match": {"char_id": char_id}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    grabbers_list = []
    counter = 1
    async for entry in claims.aggregate(pipeline):
        try:
            user_id = entry["_id"]
            user = await client.get_users(user_id)
            user_name = html.escape(user.first_name)
            grabbers_list.append(f"{counter}. <a href='tg://user?id={user_id}'>{user_name}</a> ⪼ x{entry['count']}")
            counter += 1
        except:
            grabbers_list.append(f"{counter}. Unknown User ⪼ x{entry['count']}")
            counter += 1

    grabbers_text = "\n".join(grabbers_list) if grabbers_list else "No grabbers yet."

    # Final Caption Construction
    caption = (
        f"🔍 <b>Cʜᴀʀᴀᴄᴛᴇʀ Dᴇᴛᴀɪʟs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>ID:</b> <code>{char.get('id')}</code>\n"
        f"👤 <b>Nᴀᴍᴇ:</b> {html.escape(char.get('name'))}\n"
        f"🎌 <b>Aɴɪᴍᴇ:</b> {html.escape(char.get('anime'))}\n"
        f"✨ <b>Rᴀʀɪᴛʏ:</b> {html.escape(char.get('rarity', 'Common ⚪️'))}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>Tᴏᴘ 10 Gʀᴀʙʙᴇʀs:</b>\n"
        f"{grabbers_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

file_id = char.get('file_id') or char.get('img_url') or char.get('image')
    is_video = char.get("is_video", False) 

    try:
        if file_id:
            if is_video:
                # Send as Video for AMVs
                await message.reply_video(
                    video=file_id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML
                )
            else:
                # Send as Photo for others
                await message.reply_photo(
                    photo=file_id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML
                )
        else:
            # If no file_id exists, we must use reply_text
            # reply_text does NOT take a 'caption' argument, it takes 'text'
            await message.reply_text(
                text=caption, 
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Media Send Error: {e}")
        # Final fallback if Telegram rejects the file_id
        await message.reply_text(text=caption, parse_mode=ParseMode.HTML)
