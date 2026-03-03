from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import groups, settings as global_settings # Assuming 'settings' collection exists
from config import OWNER_ID

# --- HELPER FUNCTIONS ---
async def get_config(chat_id):
    # Check for Global Overrides first
    g_config = await global_settings.find_one({"_id": "GLOBAL_CONFIG"}) or {}
    
    # Check for Local Group settings
    l_config = await groups.find_one({"_id": chat_id}) or {"grab": True, "antispam": False}
    
    return g_config, l_config

@Client.on_message(filters.command("settings"))
async def group_settings_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return 

    g_cfg, l_cfg = await get_config(message.chat.id)
    
    # Global Status
    g_grab = "✅" if g_cfg.get("global_grab", True) else "❌"
    g_spam = "✅" if g_cfg.get("global_spam", False) else "❌"
    
    # Local Status
    l_grab = "✅" if l_cfg.get("grab", True) else "❌"
    l_spam = "✅" if l_cfg.get("antispam", False) else "❌"

    text = (
        f"⚙️ **Bᴏᴛ Oᴡɴᴇʀ Cᴏɴᴛʀᴏʟ Pᴀɴᴇʟ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 **GLOBAL (All Groups)**\n"
        f"🌸 Spawning: {g_grab} | 🛡️ Anti-Spam: {g_spam}\n\n"
        f"📍 **LOCAL (This Group)**\n"
        f"🌸 Spawning: {l_grab} | 🛡️ Anti-Spam: {l_spam}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    buttons = [
        [InlineKeyboardButton(f"🌍 Toggle Global Grab: {g_grab}", callback_data="set_g_grab")],
        [InlineKeyboardButton(f"🌍 Toggle Global Spam: {g_spam}", callback_data="set_g_spam")],
        [InlineKeyboardButton("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯", callback_data="none")],
        [InlineKeyboardButton(f"📍 Toggle Local Grab: {l_grab}", callback_data=f"set_l_grab_{message.chat.id}")],
        [InlineKeyboardButton(f"📍 Toggle Local Spam: {l_spam}", callback_data=f"set_l_spam_{message.chat.id}")]
    ]
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^set_"))
async def toggle_settings(client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("❌ Owner Only!", show_alert=True)

    data = query.data.split("_")
    scope = data[1] # 'g' for global, 'l' for local
    action = data[2]
    
    g_cfg, _ = await get_config(query.message.chat.id)

    if scope == "g":
        # Handle Global Toggle
        field = "global_grab" if action == "grab" else "global_spam"
        new_val = not g_cfg.get(field, True if action == "grab" else False)
        await global_settings.update_one({"_id": "GLOBAL_CONFIG"}, {"$set": {field: new_val}}, upsert=True)
    
    else:
        # Handle Local Toggle
        chat_id = int(data[3])
        l_cfg = await groups.find_one({"_id": chat_id}) or {"grab": True, "antispam": False}
        field = "grab" if action == "grab" else "antispam"
        new_val = not l_cfg.get(field, True if action == "grab" else False)
        await groups.update_one({"_id": chat_id}, {"$set": {field: new_val}}, upsert=True)

    # UI Refresh Logic
    g_cfg, l_cfg = await get_config(query.message.chat.id)
    g_grab = "✅" if g_cfg.get("global_grab", True) else "❌"
    g_spam = "✅" if g_cfg.get("global_spam", False) else "❌"
    l_grab = "✅" if l_cfg.get("grab", True) else "❌"
    l_spam = "✅" if l_cfg.get("antispam", False) else "❌"

    await query.message.edit_text(
        f"⚙️ **Bᴏᴛ Oᴡɴᴇʀ Cᴏɴᴛʀᴏʟ Pᴀɴᴇʟ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 **GLOBAL (All Groups)**\n"
        f"🌸 Spawning: {g_grab} | 🛡️ Anti-Spam: {g_spam}\n\n"
        f"📍 **LOCAL (This Group)**\n"
        f"🌸 Spawning: {l_grab} | 🛡️ Anti-Spam: {l_spam}\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🌍 Toggle Global Grab: {g_grab}", callback_data="set_g_grab")],
            [InlineKeyboardButton(f"🌍 Toggle Global Spam: {g_spam}", callback_data="set_g_spam")],
            [InlineKeyboardButton("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯", callback_data="none")],
            [InlineKeyboardButton(f"📍 Toggle Local Grab: {l_grab}", callback_data=f"set_l_grab_{query.message.chat.id}")],
            [InlineKeyboardButton(f"📍 Toggle Local Spam: {l_spam}", callback_data=f"set_l_spam_{query.message.chat.id}")]
        ])
    )
    await query.answer("Global Settings Updated!" if scope == "g" else "Local Settings Updated!")