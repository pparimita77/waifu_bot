import asyncio
from pyrogram import Client, filters
from database import characters, db, settings
from handlers.spawnrate import get_global_spawnrate 

message_counts = {}

async def get_global_rarities():
    """Fetches and cleans the allowed rarities list"""
    data = await settings.find_one({"_id": "global_spawn_settings"})
    if not data or "rarities" not in data:
        return [] # Return empty to prevent any spawn if settings are broken
    
    # Ensure all strings are stripped of hidden spaces
    return [str(r).strip() for r in data["rarities"]]

@Client.on_message(filters.group & ~filters.bot)
async def auto_spawner(client, message):
    chat_id = int(message.chat.id)
    
    threshold = await get_global_spawnrate()
    enabled_rarities = await get_global_rarities()

    if chat_id not in message_counts:
        message_counts[chat_id] = 0
    message_counts[chat_id] += 1

    if message_counts[chat_id] >= threshold:
        message_counts[chat_id] = 0 
        
        # 1. STOP if no rarities are enabled
        if not enabled_rarities:
            print("⚠️ Spawn attempted but ALL rarities are locked in database.")
            return 

        # 2. THE FORCE FILTER
        # Using a regex-based $in to handle any accidental case sensitivity issues
        import re
        regex_list = [re.compile(f"^{re.escape(r)}$", re.IGNORECASE) for r in enabled_rarities]

        pipeline = [
            {"$match": {"rarity": {"$in": regex_list}}},
            {"$sample": {"size": 1}}
        ]
        
        results = await characters.aggregate(pipeline).to_list(1)
        
        if not results:
            print(f"⚠️ No characters found matching enabled rarities: {enabled_rarities}")
            return 

        char = results[0]

        # 3. Save to active spawns
        await db.spawned_waifus.update_one(
            {"chat_id": chat_id},
            {"$set": {
                "char_id": char['id'], 
                "name": char['name'], 
                "rarity": char['rarity'], 
                "anime": char['anime']
            }},
            upsert=True
        )

        # 4. Standalone Spawn (No Reply)
        caption = (
            "🌸 <b>A Gᴇɴᴛʟᴇ Gʟᴏᴡ Fɪʟʟs Tʜᴇ Sᴘᴀᴄᴇ.</b>\n"
            "<b>Sᴏᴍᴇᴛʜɪɴɢ Pʀᴇᴄɪᴏᴜs Aᴘᴘʀᴏᴀᴄʜᴇs—</b>\n\n"
            "<b>A Wᴀɪғᴜ Hᴀs Aᴘᴘᴇᴀʀᴇᴅ 💖</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Usᴇ /grab Tᴏ Cᴏʟʟᴇᴄᴛ Hᴇʀ"
        )
        
        try:
            file_id = char.get('file_id') or char.get('image')
            is_video = char.get("is_video", False) 

            if is_video:
                spawn_msg = await client.send_video(chat_id=chat_id, video=file_id, caption=caption)
            else:
                spawn_msg = await client.send_photo(chat_id=chat_id, photo=file_id, caption=caption)
            
            asyncio.create_task(auto_delete_spawn(client, chat_id, char['id'], spawn_msg))
            
        except Exception as e:
            print(f"❌ SPAWN ERROR: {e}")

async def auto_delete_spawn(client, chat_id, char_id, spawn_msg):
    await asyncio.sleep(300) 
    still_there = await db.spawned_waifus.find_one({"chat_id": chat_id, "char_id": char_id})
    if still_there:
        await db.spawned_waifus.delete_one({"chat_id": chat_id})
        try:
            await spawn_msg.edit_caption("<b>🕒 Tʜᴇ ᴡᴀɪғᴜ ʜᴀs ᴅɪsᴀᴘᴘᴇᴀʀᴇᴅ ɪɴᴛᴏ ᴛʜᴇ ᴍɪsᴛ...</b>")
        except:
            pass