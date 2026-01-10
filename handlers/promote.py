from pyrogram import Client, filters
from database import staff
from sudo import is_owner, OWNER_ID

@Client.on_message(filters.command("promote") & is_owner)
async def promote_user(client, message):
    # Usage: /promote sudo (while replying)
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to the user you want to promote!")

    # Determine Role (default to sudo)
    role = "sudo"
    if len(message.command) > 1:
        role = message.command[1].lower()
    
    allowed_roles = ["sudo", "dev", "uploader"]
    if role not in allowed_roles:
        return await message.reply_text(f"❌ Invalid role! Use: {', '.join(allowed_roles)}")

    user = message.reply_to_message.from_user
    
    # Save to MongoDB
    await staff.update_one(
        {"_id": user.id},
        {"$set": {
            "name": user.first_name,
            "role": role
        }},
        upsert=True
    )

    await message.reply_text(
        f"✅ **Pʀᴏᴍᴏᴛɪᴏɴ Sᴜᴄᴄᴇssғᴜʟ!**\n\n"
        f"👤 **User:** {user.mention}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🎖️ **Role:** `{role.upper()}`"
    )

@Client.on_message(filters.command("demote") & is_owner)
async def demote_user(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to the user you want to demote!")

    user = message.reply_to_message.from_user
    result = await staff.delete_one({"_id": user.id})

    if result.deleted_count > 0:
        await message.reply_text(f"✅ {user.mention} has been removed from the staff list.")
    else:
        await message.reply_text("❌ This user is not a staff member.")