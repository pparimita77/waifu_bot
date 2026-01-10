import random
from pyrogram import Client, filters
from database import characters, settings, groups
from vars import active_spawns, message_counts

@Client.on_message(filters.group & ~filters.bot)
async def auto_spawn_handler(client, message):
    chat_id = message.chat.id
    
    # --- FIX: Moved inside the function ---
    # Check if 'grab' is enabled for this specific group
    group_settings = await groups.find_one({"_id": chat_id})
    if group_settings and group_settings.get("grab") is False:
        return  # The bot is silent in this group
    
    # Increment counter
    message_counts[chat_id] = message_counts.get(chat_id, 0) + 1
    
    if message_counts[chat_id] >= 100:
        message_counts[chat_id] = 0 
        
        # Check wmode from settings collection
        mode_doc = await settings.find_one({"_id": "spawn_mode"})
        mode = mode_doc.get("mode", "all") if mode_doc else "all"

        # Filter characters by rarity if mode is not 'all'
        query = {} if mode == "all" else {"rarity": mode}
        all_chars = await characters.find(query).to_list(length=None)

        if not all_chars:
            all_chars = await characters.find({}).to_list(length=None)

        if all_chars:
            char = random.choice(all_chars)
            active_spawns[chat_id] = char # Store for /grab
            
            # Your New Updated Message
            caption = (
                "🌸 **A Gᴇɴᴛʟᴇ Gʟᴏᴡ Fɪʟʟs Tʜᴇ Sᴘᴀᴄᴇ.**\n"
                "Sᴏᴍᴇᴛʜɪɴɢ Pʀᴇᴄɪᴏᴜs Aᴘᴘʀᴏᴀᴄʜᴇs—\n\n"
                "**A Wᴀɪғᴜ Hᴀs Aᴘᴘᴇᴀʀᴇᴅ💖.**\n"
                "Usᴇ `/grab <ɴᴀᴍᴇ>` ᴛᴏ ᴄᴏʟʟᴇᴄᴛ!"
            )
            
            await message.reply_photo(photo=char['file_id'], caption=caption)