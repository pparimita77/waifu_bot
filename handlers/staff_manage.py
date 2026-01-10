from pyrogram import Client, filters
from database import staff
from sudo import OWNER_ID

@Client.on_message(filters.command(["promote", "addstaff"]) & filters.user(OWNER_ID))
async def promote_user(client, message):
    if len(message.command) < 3:
        return await message.reply_text("📜 **Usᴀɢᴇ:** `/promote <user_id> <dev|sudo|uploader>`")

    try:
        user_id = int(message.command[1])
        role = message.command[2].lower()
    except ValueError:
        return await message.reply_text("❌ User ID must be a number.")

    if role not in ["dev", "sudo", "uploader"]:
        return await message.reply_text("❌ Invalid role. Use: `dev`, `sudo`, or `uploader`.")

    # Save to database
    await staff.update_one(
        {"_id": user_id},
        {"$set": {"role": role}},
        upsert=True
    )
    
    await message.reply_text(f"✅ User `{user_id}` has been promoted to **{role.upper()}**.")

@Client.on_message(filters.command(["demote", "removestaff"]) & filters.user(OWNER_ID))
async def demote_user(client, message):
    if len(message.command) < 2:
        return await message.reply_text("📜 **Usᴀɢᴇ:** `/demote <user_id>`")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ User ID must be a number.")

    result = await staff.delete_one({"_id": user_id})

    if result.deleted_count > 0:
        await message.reply_text(f"🗑️ User `{user_id}` has been removed from the staff list.")
    else:
        await message.reply_text("❌ User not found in staff list.")