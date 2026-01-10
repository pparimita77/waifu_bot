from pyrogram import Client, filters  # <--- THIS WAS MISSING
from database import staff
from sudo import OWNER_ID, is_sudo

@Client.on_message(filters.command("staff"))
async def list_staff(client, message):
    all_staff = await staff.find().to_list(length=100)
    
    if not all_staff:
        return await message.reply_text("📝 No staff members found besides the Owner.")

    text = "👥 **Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ Sᴛᴀғғ Lɪsᴛ**\n━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👑 **Owner:** `{OWNER_ID}`\n\n"

    # Categorize by role
    for member in all_staff:
        role_icon = "🛠️" if member['role'] == "dev" else "🛡️" if member['role'] == "sudo" else "📤"
        text += f"{role_icon} **{member['role'].upper()}**: {member['name']} (`{member['_id']}`)\n"

    await message.reply_text(text)