import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import characters, staff
from config import OWNER_ID, DEVS

# --- CONFIGURATION ---
LOG_CHANNEL_ID = -1003350651929 
LOG_CHANNEL_LINK = "https://t.me/Tomioka_giyu_uploader13" 

RARITIES = {
    "1": "Common ⚪️", "2": "Legendary 💮", "3": "Rare 🍁", 
    "4": "Special 🫧", "5": "Limited 🔮", "6": "Celestial 🎐",
    "7": "Manga 🔖", "8": "Expensive 💸", "9": "Demonic ☠",
    "10": "Royal 👑", "11": "Summer 🏝️", "12": "Winter ❄️",
    "13": "Valentine 💝", "14": "Seasonal 🍂", "15": "Halloween 🎃",
    "16": "Christmas 🎄", "17": "AMV 🎥"
}

# Ensure AUTHORIZED is a flat list of integers
AUTHORIZED_IDS = [OWNER_ID] if not isinstance(OWNER_ID, list) else OWNER_ID
if DEVS:
    AUTHORIZED_IDS += DEVS if isinstance(DEVS, list) else [DEVS]

@Client.on_message(filters.command("cupload"))
async def cupload_handler(client, message):
    user_id = message.from_user.id
    
    # 1. Authorization Check
    is_authorized = user_id in AUTHORIZED_IDS
    if not is_authorized:
        user_staff = await staff.find_one({"_id": user_id})
        if user_staff and user_staff.get("role") in ["sudo", "dev", "uploader"]:
            is_authorized = True
    
    if not is_authorized:
        return await message.reply_text("🚫 <b>Access Denied!</b>", parse_mode=ParseMode.HTML)

    # 2. Validation
    reply = message.reply_to_message
    if not reply or (not reply.photo and not reply.video):
        return await message.reply_text("❌ <b>Reply to a Photo or Video!</b>", parse_mode=ParseMode.HTML)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ <b>Usage:</b>\n<code>/cupload Name | Anime | Rarity_ID</code>", 
            parse_mode=ParseMode.HTML
        )

    try:
        args = message.text.split(" ", 1)[1].split("|")
        name = args[0].strip()
        anime = args[1].strip()
        rarity_idx = args[2].strip()
        provided_id = args[3].strip() if len(args) > 3 else None

        rarity = RARITIES.get(rarity_idx)
        if not rarity:
            return await message.reply_text("❌ <b>Invalid Rarity ID (1-17)!</b>", parse_mode=ParseMode.HTML)

        file_id = reply.video.file_id if reply.video else reply.photo.file_id
        is_video = bool(reply.video)

        # 3. Smart ID Generation (Gap Filling Logic)
        is_update = False
        if provided_id:
            existing = await characters.find_one({"id": provided_id})
            char_id = provided_id
            if existing:
                is_update = True
        else:
            # Fetch all existing IDs as integers
            all_chars = await characters.find({}, {"id": 1}).to_list(length=None)
            existing_ids = sorted([int(c["id"]) for c in all_chars if c["id"].isdigit()])
            
            if not existing_ids:
                char_id = "1"
            else:
                # Find the first gap in the sequence
                # e.g., if IDs are [1, 2, 4, 5], it finds 3
                new_id_int = 1
                for eid in existing_ids:
                    if new_id_int < eid:
                        break
                    new_id_int = eid + 1
                char_id = str(new_id_int)

        char_data = {
            "id": char_id,
            "name": name,
            "anime": anime,
            "rarity": rarity,
            "file_id": file_id,
            "is_video": is_video,
            "uploader_id": user_id
        }

        if is_update:
            await characters.update_one({"id": char_id}, {"$set": char_data})
            header = "<b>✨ CHARACTER UPDATED ✨</b>"
        else:
            await characters.insert_one(char_data)
            header = "<b>🌸 NEW CHARACTER UPLOADED 🌸</b>"

        # 4. Formatted Log Caption
        log_caption = (
            f"{header}\n"
            "<b>━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<b>🎭 Nᴀᴍᴇ:</b> {html.escape(name)}\n"
            f"<b>📺 Sᴇʀɪᴇꜱ:</b> {html.escape(anime)}\n"
            f"<b>🆔 Iᴅ:</b> <code>{char_id}</code>\n"
            f"<b>💫 Rᴀʀɪᴛʏ:</b> {rarity}\n"
            "<b>━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<b>👤 Uᴘʟᴏᴀᴅᴇʀ:</b> {message.from_user.mention}"
        )

        if is_video:
            await client.send_video(LOG_CHANNEL_ID, video=file_id, caption=log_caption)
        else:
            await client.send_photo(LOG_CHANNEL_ID, photo=file_id, caption=log_caption)

        await message.reply_text(
            f"✅ <b>ID: {char_id}</b> {'Updated' if is_update else 'Uploaded'}!",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        # Use html.escape to prevent the error message itself from crashing the bot
        error_msg = html.escape(str(e))
        await message.reply_text(f"❌ <b>Error:</b> <code>{error_msg}</code>", parse_mode=ParseMode.HTML)