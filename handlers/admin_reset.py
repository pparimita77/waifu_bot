import html
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import OWNER_ID, DEVS
from database import users, claims

# Create a flat list of authorized IDs for filters and callback checks
AUTHORIZED = [OWNER_ID] if not isinstance(OWNER_ID, list) else OWNER_ID
if DEVS:
    AUTHORIZED += DEVS if isinstance(DEVS, list) else [DEVS]

# Shortening callback prefixes to avoid Telegram's 64-byte limit
# kb = kill_bal, kc = kill_char

@Client.on_message(filters.command("kill_bal") & filters.user(AUTHORIZED))
async def kill_bal_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b>\n"
            "<code>/kill_bal whole</code> - Reset everyone\n"
            "<code>/kill_bal emerald</code> - Reset all emeralds\n"
            "<code>/kill_bal [user_id] [mode]</code>",
            parse_mode=ParseMode.HTML
        )

    cmd = message.command
    if cmd[1].isdigit():
        target_id = int(cmd[1])
        mode = cmd[2].lower() if len(cmd) > 2 else "whole"
        cb_data = f"kb_{target_id}_{mode}"
        text = f"🚨 <b>Confirm Reset for User {target_id}?</b>\nMode: <code>{mode.upper()}</code>"
    else:
        mode = cmd[1].lower()
        cb_data = f"kb_all_{mode}"
        text = f"🚨 <b>Confirm GLOBAL Reset?</b>\nMode: <code>{mode.upper()}</code>"

    buttons = [[
        InlineKeyboardButton("✅ Wipe", callback_data=cb_data),
        InlineKeyboardButton("❌ Cancel", callback_data="k_c")
    ]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

@Client.on_message(filters.command("kill_char") & filters.user(AUTHORIZED))
async def kill_char_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b>\n"
            "<code>/kill_char whole</code> - Wipe ALL harems globally\n"
            "<code>/kill_char [char_id]</code> - Remove 1 char from everyone\n"
            "<code>/kill_char [user_id] whole</code> - Wipe 1 user's harem\n"
            "<code>/kill_char [user_id] [char_id]</code> - Remove 1 char from 1 user",
            parse_mode=ParseMode.HTML
        )

    cmd = message.command
    if cmd[1].isdigit() and len(cmd) > 2:
        target_user = cmd[1]
        target_char = cmd[2]
        cb_data = f"kc_{target_user}_{target_char}"
        text = f"🚨 <b>Confirm Delete for User {target_user}?</b>\nTarget: <code>{target_char}</code>"
    else:
        target_val = cmd[1]
        cb_data = f"kc_all_{target_val}"
        text = f"🚨 <b>Confirm GLOBAL Delete?</b>\nTarget: <code>{target_val}</code>"

    buttons = [[
        InlineKeyboardButton("✅ Delete", callback_data=cb_data),
        InlineKeyboardButton("❌ Cancel", callback_data="k_c")
    ]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

# --- CALLBACK HANDLERS ---

@Client.on_callback_query(filters.regex(r"^(kb_|kc_|k_c)"))
async def handle_admin_wipes(client, query):
    # Updated to check membership in the AUTHORIZED list
    if query.from_user.id not in AUTHORIZED:
        return await query.answer("Unauthorized", show_alert=True)

    if query.data == "k_c":
        return await query.message.edit_text("❌ <b>Action Cancelled.</b>", parse_mode=ParseMode.HTML)

    data = query.data.split("_")
    prefix = data[0]
    target = data[1]
    val = data[2]

    if prefix == "kb":
        filt = {} if target == "all" else {"$or": [{"user_id": int(target)}, {"_id": int(target)}]}
        
        if val == "whole": update = {"$set": {"emeralds": 0, "stardust": 0.0}}
        elif val == "emerald": update = {"$set": {"emeralds": 0}}
        elif val == "stardust": update = {"$set": {"stardust": 0.0}}
        else: update = {"$set": {"emeralds": 0}} # Default fallback
        
        await users.update_many(filt, update)
        await query.message.edit_text(f"✅ <b>Balance reset complete for:</b> <code>{target}</code>", parse_mode=ParseMode.HTML)

    elif prefix == "kc":
        filt = {}
        if target != "all":
            filt["user_id"] = int(target)
        if val != "whole":
            filt["char_id"] = val
            
        result = await claims.delete_many(filt)
        await query.message.edit_text(
            f"🗑 <b>Wipe Complete!</b>\nRemoved <code>{result.deleted_count}</code> characters from harem database.",
            parse_mode=ParseMode.HTML
        )

    await query.answer()