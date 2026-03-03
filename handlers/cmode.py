import html
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users

# Updated to 17 Rarities with matching emojis
RARITIES = {
    "Common": "⚪️", "Legendary": "💮", "Rare": "🍁", 
    "Special": "🫧", "Limited": "🔮", "Celestial": "🎐",
    "Manga": "🔖", "Expensive": "💸", "Demonic": "☠", 
    "Royal": "👑", "Summer": "🏝️", "Winter": "❄️",
    "Valentine": "💝", "Seasonal": "🍂", "Halloween": "🎃",
    "Christmas": "🎄", "AMV": "🎥"
}

@Client.on_message(filters.command("cmode") & filters.group, group=0)
async def cmode_command(client, message):
    if not message.from_user:
        return

    buttons = []
    rarity_keys = list(RARITIES.keys())

    # 2-column grid layout for 17 rarities
    for i in range(0, len(rarity_keys), 2):
        row = [
            InlineKeyboardButton(
                f"{RARITIES[r]} {r}", 
                callback_data=f"cmode_{r}"
            ) 
            for r in rarity_keys[i:i+2]
        ]
        buttons.append(row)

    # Added 'Show All' at the bottom
    buttons.append([InlineKeyboardButton("✨ Sʜᴏᴡ Aʟʟ (Dᴇғᴀᴜʟᴛ)", callback_data="cmode_all")])

    await message.reply_text(
        f"✨ **Cᴏʟʟᴇᴄᴛɪᴏɴ Dɪsᴘʟᴀʏ Mᴏᴅᴇ**\n\n"
        f"👤 **User:** {message.from_user.first_name}\n"
        "Sᴇʟᴇᴄᴛ ᴀ ʀᴀʀɪᴛʏ ᴛᴏ ғɪʟᴛᴇʀ ʏᴏᴜʀ `/harem` view:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^cmode_"))
async def set_cmode(client, query):
    try:
        mode = query.data.split("_")[1]
        user_id = query.from_user.id

        # Security check
        if query.message.reply_to_message and query.message.reply_to_message.from_user.id != user_id:
            return await query.answer("❌ This menu is not for you!", show_alert=True)
        
        # Database Update
        await users.update_one(
            {"$or": [{"user_id": user_id}, {"_id": user_id}, {"id": user_id}]},
            {"$set": {"harem_mode": mode}},
            upsert=True
        )
        
        display_name = mode.upper() if mode != "all" else "ALL"
        await query.answer(f"✅ Harem Mode: {display_name}")
        
        # Confirmation text
        symbol = RARITIES.get(mode, "✨")
        await query.message.edit_text(
            f"✅ **Sᴇᴛᴛɪɴɢ Sᴀᴠᴇᴅ!**\n\n"
            f"👤 **User:** {query.from_user.first_name}\n"
            f"🖼️ **Mode:** {symbol} {display_name}\n\n"
            "Yᴏᴜʀ `/harem` ᴡɪʟʟ ɴᴏᴡ ʙᴇ ғɪʟᴛᴇʀᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ."
        )
    except Exception as e:
        print(f"Error in cmode: {e}")
        await query.answer("❌ Error saving preference.", show_alert=True)