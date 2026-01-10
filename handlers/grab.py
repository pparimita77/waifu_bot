from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import claims
from vars import active_spawns
import datetime

@Client.on_message(filters.command("grab"))
async def grab_waifu(client, message):
    chat_id = message.chat.id
    
    if chat_id not in active_spawns:
        return await message.reply_text("🌸 No Waifu has appeared yet! Wait for the next spawn.")

    try:
        guess = message.text.split(None, 1)[1].strip().lower()
    except IndexError:
        return await message.reply_text("Pʟᴇᴀsᴇ Pʀᴏᴠɪᴅᴇ A Nᴀᴍᴇ! Usᴀɢᴇ: /grab <name>")

    target_waifu = active_spawns[chat_id]
    
    if guess == target_waifu['name'].lower():
        # Save to claims for /harem
        await claims.insert_one({
            "user_id": message.from_user.id,
            "char_id": target_waifu['id'],
            "date": datetime.datetime.now()
        })
        
        del active_spawns[chat_id] # Prevent double grabbing

        text = (
            "**Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs 🥳**\n\n"
            "🌊 Yᴏᴜʀ Tɪᴍɪɴɢ Wᴀs Pᴇʀғᴇᴄᴛ.\n"
            "Tʜᴇ Gʀᴀʙ Wᴀs Sᴜᴄᴄᴇssғᴜʟ 💙\n\n"
            f"✨ **Nᴀᴍᴇ:** {target_waifu['name']}\n"
            f"🆔 **Iᴅ:** `{target_waifu['id']}`\n"
            f"🎌 **Sᴏᴜʀᴄᴇ:** {target_waifu['anime']}"
        )
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("💕 Cᴏʟʟᴇᴄᴛɪᴏɴs 💕", callback_data="harem_1")
        ]])
        
        await message.reply_text(text, reply_markup=keyboard)
    else:
        await message.reply_text("❌ Iɴᴄᴏʀʀᴇᴄᴛ Nᴀᴍᴇ. Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ.")