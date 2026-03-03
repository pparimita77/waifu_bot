import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import characters, claims
from config import OWNER_ID, DEVS 

# Flatten AUTHORIZED list for cleaner checks
AUTHORIZED = [OWNER_ID] if not isinstance(OWNER_ID, list) else OWNER_ID
if DEVS:
    AUTHORIZED += DEVS if isinstance(DEVS, list) else [DEVS]

@Client.on_message(filters.command("delete"))
async def delete_character(client, message):
    user_id = message.from_user.id
    
    # --- AUTHORIZATION FIX ---
    if user_id not in AUTHORIZED:
        return await message.reply_text("🚫 <b>Bhk.</b>", parse_mode=ParseMode.HTML)

    # --- USAGE FIX (Using HTML entities for < and >) ---
    if len(message.command) < 2:
        return await message.reply_text(
            "🗑️ <b>Usᴀɢᴇ:</b> <code>/delete &lt;char_id&gt;</code>",
            parse_mode=ParseMode.HTML
        )

    char_id = message.command[1]

    # 1. Find the character first to confirm details
    char_to_delete = await characters.find_one({"id": char_id})
    
    if not char_to_delete:
        return await message.reply_text(
            f"❌ Character ID <code>{html.escape(char_id)}</code> not found.",
            parse_mode=ParseMode.HTML
        )

    # Escape names to prevent parsing errors
    char_name = html.escape(char_to_delete.get("name", "Unknown"))
    char_anime = html.escape(char_to_delete.get("anime") or char_to_delete.get("animee", "Unknown"))

    # 2. Delete from collections
    await characters.delete_one({"id": char_id})
    await claims.delete_many({"char_id": char_id})

    # 3. Final Response
    caption = (
        f"🗑️ <b>Cʜᴀʀᴀᴄᴛᴇʀ Dᴇʟᴇᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌸 <b>Nᴀᴍᴇ:</b> {char_name}\n"
        f"🆔 <b>Iᴅ:</b> <code>{char_id}</code>\n"
        f"🍜 <b>Sᴏᴜʀᴄᴇ:</b> {char_anime}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <i>Aʟʟ ᴇxɪsᴛɪɴɢ ᴄʟᴀɪᴍs ʜᴀᴠᴇ ʙᴇᴇɴ ᴘᴜʀɢᴇᴅ.</i>"
    )

    await message.reply_text(caption, parse_mode=ParseMode.HTML)