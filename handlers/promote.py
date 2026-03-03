import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import staff
from config import OWNER_ID, DEVS
from auth_utils import AUTHORIZED  # Import the clean list

@Client.on_message(filters.command("promote") & filters.user(AUTHORIZED))
async def promote_user(client, message):
    # Usage: /promote sudo (while replying)
    if not message.reply_to_message:
        return await message.reply_text("❌ <b>Reply to the user you want to promote!</b>")

    # Determine Role (default to sudo)
    role = "sudo"
    if len(message.command) > 1:
        role = message.command[1].lower()
    
    allowed_roles = ["sudo", "dev", "uploader"]
    if role not in allowed_roles:
        return await message.reply_text(f"❌ <b>Invalid role!</b> Use: <code>{', '.join(allowed_roles)}</code>")

    user = message.reply_to_message.from_user
    # Escape name to prevent HTML breaking if user has '<' in their name
    safe_name = html.escape(user.first_name)

    # Save to MongoDB
    await staff.update_one(
        {"_id": user.id},
        {"$set": {
            "name": user.first_name,
            "role": role
        }},
        upsert=True
    )

    # We use HTML style here to avoid "Entity Bounds" errors
    await message.reply_text(
        f"✅ <b>Pʀᴏᴍᴏᴛɪᴏɴ Sᴜᴄᴄᴇssғᴜʟ!</b>\n\n"
        f"👤 <b>User:</b> <a href='tg://user?id={user.id}'>{safe_name}</a>\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🎖️ <b>Role:</b> <code>{role.upper()}</code>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.command("demote") & filters.user(AUTHORIZED))
async def demote_user(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ <b>Reply to the user you want to demote!</b>")

    user = message.reply_to_message.from_user
    safe_name = html.escape(user.first_name)
    
    result = await staff.delete_one({"_id": user.id})

    if result.deleted_count > 0:
        await message.reply_text(
            f"✅ <a href='tg://user?id={user.id}'>{safe_name}</a> has been removed from the staff list.",
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text("❌ <b>This user is not a staff member.</b>")