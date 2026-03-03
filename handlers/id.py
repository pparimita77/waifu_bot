from pyrogram import Client, filters
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("id"))
async def get_id(client, message):
    # 1. If the user forwards a message to the bot
    if message.reply_to_message:
        target = message.reply_to_message
        
        # Check for forwarded channel/chat
        if target.forward_from_chat:
            id_text = (
                f"📢 Channel/Chat ID: <code>{target.forward_from_chat.id}</code>\n"
                f"👤 Title: {target.forward_from_chat.title}"
            )
        # Check for forwarded user
        elif target.forward_from:
            id_text = (
                f"👤 User ID: <code>{target.forward_from.id}</code>\n"
                f"🏷️ Name: {target.forward_from.first_name}"
            )
        # If it's just a regular reply to a message in the current chat
        else:
            id_text = (
                f"👤 User ID: <code>{target.from_user.id}</code>\n"
                f"💬 Message ID: <code>{target.id}</code>"
            )
            
    # 2. If it's just a plain /id command in a chat
    else:
        id_text = (
            f"📍 Current Chat ID: <code>{message.chat.id}</code>\n"
            f"👤 Your ID: <code>{message.from_user.id}</code>"
        )

    await message.reply_text(id_text, parse_mode=ParseMode.HTML)