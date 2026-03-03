import html
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users

# Updated Rarity List to match your exact request
RARITIES = {
    "Common": "⚪️", "Legendary": "💮", "Rare": "🏵", 
    "Special": "🫧", "Limited": "🔮", "Celestial": "🎐",
    "Manga": "🔖", "Expensive": "💸", "Giveaway": "🧧", 
    "Seasonal": "🍂", "Valentine": "💝", "AMV": "🎥"
}

@Client.on_message(filters.command("cmode") & filters.group, group=0)
async def cmode_command(client, message):
    if not message.from_user:
        return

    buttons = []
    rarity_keys = list(RARITIES.keys())

    # 2-column grid layout
    for i in range(0, len(rarity_keys), 2):
        row = [
            InlineKeyboardButton(
                f"{RARITIES[r]} {r}", 
                callback_data=f"cmv1_{r}_{message.from_user.id}"
            ) 
            for r in rarity_keys[i:i+2]
        ]
        buttons.append(row)

    # Adding the "Show All" button at the bottom
    buttons.append([InlineKeyboardButton("✨ Sʜᴏᴡ Aʟʟ", callback_data=f"cmv1_all_{message.from_user.id}")])

    await message.reply_text(
        f"✨ **Cᴏʟʟᴇᴄᴛɪᴏɴ Dɪsᴘʟᴀʏ Mᴏᴅᴇ**\n\n"
        f"👤 **User:** {message.from_user.first_name}\n"
        "Sᴇʟᴇᴄᴛ ᴀ ʀᴀʀɪᴛʏ ᴛᴏ ғɪʟᴛᴇʀ ʏᴏᴜʀ `/harem` view:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^cmv1_"))
async def set_cmode(client, query):
    try:
        data = query.data.split("_")
        mode = data[1]
        target_user_id = int(data[2])
        
        # Security: Only the command initiator can click
        if query.from_user.id != target_user_id:
            return await query.answer("❌ This menu is not for you!", show_alert=True)
        
        # Database Update: Sets the user's preferred filter
        await users.update_one(
            {"$or": [{"user_id": query.from_user.id}, {"_id": query.from_user.id}, {"id": query.from_user.id}]},
            {"$set": {"harem_mode": mode}},
            upsert=True
        )
        
        display_name = mode.upper() if mode != "all" else "ALL"
        await query.answer(f"✅ Filter set to: {display_name}")
        
        await query.message.edit_text(
            f"✅ **Sᴇᴛᴛɪɴɢ Sᴀᴠᴇᴅ!**\n\n"
            f"👤 **User:** {query.from_user.first_name}\n"
            f"🖼️ **Mode:** {display_name}\n\n"
            "Yᴏᴜʀ `/harem` ᴡɪʟʟ ɴᴏᴡ ʙᴇ ғɪʟᴛᴇʀᴇᴅ ʙʏ ᴛʜɪs ʀᴀʀɪᴛʏ."
        )
    except Exception as e:
        print(f"Error in cmode: {e}")
        await query.answer("❌ An error occurred.", show_alert=True)