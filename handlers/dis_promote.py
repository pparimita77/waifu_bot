import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import staff
from config import OWNER_ID, DEVS

# --- FLATTEN AUTHORIZED USERS ---
def get_auth_list():
    auth = []
    # Add Owner
    if isinstance(OWNER_ID, list):
        auth.extend(OWNER_ID)
    else:
        auth.append(OWNER_ID)
    # Add Devs
    if DEVS:
        if isinstance(DEVS, list):
            auth.extend(DEVS)
        else:
            auth.append(DEVS)
    # Clean up: remove duplicates and non-integers
    return list(set(int(x) for x in auth if x))

AUTHORIZED = get_auth_list()

@Client.on_message(filters.command("dis_promote") & filters.user(AUTHORIZED))
async def dis_promote_user(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ <b>Reply to the user you want to remove from staff!</b>")

    user = message.reply_to_message.from_user
    user_id = user.id
    
    # Escape name to prevent HTML parsing errors if the user has special characters
    safe_name = html.escape(user.first_name)

    # Check if user exists in the staff collection
    staff_member = await staff.find_one({"_id": user_id})
    
    if not staff_member:
        return await message.reply_text(
            f"❌ <a href='tg://user?id={user_id}'>{safe_name}</a> is not currently in the staff list.",
            parse_mode=ParseMode.HTML
        )

    # Get the role before deleting
    old_role = staff_member.get("role", "staff").upper()

    # Delete the user document from the staff collection
    result = await staff.delete_one({"_id": user_id})

    if result.deleted_count > 0:
        await message.reply_text(
            f"🚫 <b>Sᴛᴀғғ Rᴇᴍᴏᴠᴀʟ Sᴜᴄᴄᴇssғᴜʟ!</b>\n\n"
            f"👤 <b>User:</b> <a href='tg://user?id={user_id}'>{safe_name}</a>\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"🎖️ <b>Former Role:</b> <code>{old_role}</code>\n\n"
            f"✅ This user has been stripped of all staff permissions.",
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text("❌ <b>Something went wrong. User could not be removed.</b>")