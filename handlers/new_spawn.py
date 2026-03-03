import asyncio
import re
from pyrogram import Client, filters
from database import characters, db, get_enabled_spawn_rarities, groups, settings as global_settings
from handlers.spawnrate import get_global_spawnrate 

# In-memory message tracker
message_counts = {}

@Client.on_message(filters.group & ~filters.bot, group=2)
async def auto_spawner(client, message):
    chat_id = int(message.chat.id)

    # --- 1. GLOBAL & LOCAL SETTINGS CHECK ---
    # Fetch Global Config (Kill-switch)
    g_cfg = await global_settings.find_one({"_id": "GLOBAL_CONFIG"}) or {}
    if not g_cfg.get("global_grab", True):
        return # Spawning is disabled for the entire bot

    # Fetch Local Group Config
    l_cfg = await groups.find_one({"_id": chat_id}) or {}
    if not l_cfg.get("grab", True):
        return # Spawning is disabled for this specific group

    # --- 2. MESSAGE COUNTING ---
    if chat_id not in message_counts:
        message_counts[chat_id] = 0
    message_counts[chat_id] += 1

    threshold = await get_global_spawnrate()

    # --- 3. SPAWNING LOGIC ---
    if message_counts[chat_id] >= threshold:
        message_counts[chat_id] = 0 
        
        # Fetch Whitelist from /rarity command
        enabled_rarities = await get_enabled_spawn_rarities()
        if not enabled_rarities:
            return 

        # Regex to match rarities even with emojis (e.g., "Legendary" matches "Legendary 💮")
        regex_list = [re.compile(f"^{re.escape(r)}", re.IGNORECASE) for r in enabled_rarities]
        
        pipeline = [
            {"$match": {"rarity": {"$in": regex_list}}},
            {"$sample": {"size": 1}}
        ]
        
        results = await characters.aggregate(pipeline).to_list(1)
        if not results:
            return 

        char = results[0]

        # Register spawn in DB for /grab
        await db.spawned_waifus.update_one(
            {"chat_id": chat_id},
            {"$set": {
                "char_id": char['id'], 
                "name": char['name'], 
                "rarity": char['rarity'], 
                "anime": char.get('animee') or char.get('anime', 'Unknown')
            }},
            upsert=True
        )

        caption = (
            "🌸 <b>A Gᴇɴᴛʟᴇ Gʟᴏᴡ Fɪʟʟs Tʜᴇ Sᴘᴀᴄᴇ.</b>\n"
            "<b>Sᴏᴍᴇᴛʜɪɴɢ Pʀᴇᴄɪᴏᴜs Aᴘᴘʀᴏᴀᴄʜᴇs—</b>\n\n"
            "<b>A Wᴀɪғᴜ Hᴀs Aᴘᴘᴇᴀʀᴇᴅ 💖</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Usᴇ /grab Tᴏ Cᴏʟʟᴇᴄᴛ Hᴇʀ"
        )
        
        try:
            file_id = char.get('file_id') or char.get('image') or char.get('img_url')
            
            # Strictly Photo (No Video)
            spawn_msg = await client.send_photo(
                chat_id=chat_id, 
                photo=file_id, 
                caption=caption
            )
            
            # Start background task to delete/expire spawn
            asyncio.create_task(auto_delete_spawn(client, chat_id, char['id'], spawn_msg))
            
        except Exception as e:
            print(f"❌ SPAWN ERROR: {e}")

async def auto_delete_spawn(client, chat_id, char_id, spawn_msg):
    """Wait 5 minutes, then expire the waifu if not grabbed."""
    await asyncio.sleep(300) 
    
    still_there = await db.spawned_waifus.find_one({"chat_id": chat_id, "char_id": char_id})
    if still_there:
        await db.spawned_waifus.delete_one({"chat_id": chat_id})
        try:
            await spawn_msg.edit_caption("<b>🕒 Tʜᴇ ᴡᴀɪғᴜ ʜᴀs ᴅɪsᴀᴘᴘᴇᴀʀᴇᴅ ɪɴᴛᴏ ᴛʜᴇ ᴍɪsᴛ...</b>")
        except:
            pass