from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import groups
from sudo import OWNER_ID

# --- HELPER FUNCTION ---
async def get_group_settings(chat_id):
    settings = await groups.find_one({"_id": chat_id})
    if not settings:
        return {"grab": True, "antispam": False}
    return settings

@Client.on_message(filters.command("settings") & filters.group)
async def group_settings_cmd(client, message):
    user_id = message.from_user.id
    
    # STRICT OWNER-ONLY CHECK
    if user_id != OWNER_ID:
        # Bot ignores command if not from Owner
        return 

    settings = await get_group_settings(message.chat.id)
    grab_status = "✅ Enabled" if settings.get("grab", True) else "❌ Disabled"
    spam_status = "✅ Enabled" if settings.get("antispam", False) else "❌ Disabled"

    text = (
        f"⚙️ **Bᴏᴛ Oᴡɴᴇʀ Cᴏɴᴛʀᴏʟ Pᴀɴᴇʟ**\n"
        f"Cʜᴀᴛ: {message.chat.title}\n\n"
        f"🌸 **Gʀᴀʙ (Sᴘᴀᴡɴɪɴɢ):** {grab_status}\n"
        f"🛡️ **Aɴᴛɪ-Sᴘᴀᴍ:** {spam_status}\n"
    )

    buttons = [
        [InlineKeyboardButton(f"Toggle Grab: {grab_status}", callback_data=f"set_grab_{message.chat.id}")],
        [InlineKeyboardButton(f"Toggle Anti-Spam: {spam_status}", callback_data=f"set_spam_{message.chat.id}")]
    ]
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^set_"))
async def toggle_settings(client, query: CallbackQuery):
    user_id = query.from_user.id
    
    # Only Bot Owner can click buttons
    if user_id != OWNER_ID:
        return await query.answer("❌ This menu is for the Bot Owner only.", show_alert=True)

    data = query.data.split("_")
    action = data[1]
    chat_id = int(data[2])
    
    settings = await get_group_settings(chat_id)

    if action == "grab":
        new_val = not settings.get("grab", True)
        await groups.update_one({"_id": chat_id}, {"$set": {"grab": new_val}}, upsert=True)
    elif action == "spam":
        new_val = not settings.get("antispam", False)
        await groups.update_one({"_id": chat_id}, {"$set": {"antispam": new_val}}, upsert=True)

    # Refresh Menu
    new_settings = await get_group_settings(chat_id)
    grab_status = "✅ Enabled" if new_settings.get("grab", True) else "❌ Disabled"
    spam_status = "✅ Enabled" if new_settings.get("antispam", False) else "❌ Disabled"

    await query.message.edit_text(
        f"⚙️ **Bᴏᴛ Oᴡɴᴇʀ Cᴏɴᴛʀᴏʟ Pᴀɴᴇʟ**\n\n"
        f"🌸 **Gʀᴀʙ (Sᴘᴀᴡɴɪɴɢ):** {grab_status}\n"
        f"🛡️ **Aɴᴛɪ-Sᴘᴀᴍ:** {spam_status}\n",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Toggle Grab: {grab_status}", callback_data=f"set_grab_{chat_id}")],
            [InlineKeyboardButton(f"Toggle Anti-Spam: {spam_status}", callback_data=f"set_spam_{chat_id}")]
        ])
    )
    await query.answer("Preference Saved!")