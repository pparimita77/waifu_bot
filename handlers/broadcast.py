import asyncio
from pyrogram import Client, filters
from database import users
from sudo import is_owner  # This requires sudo.py to exist!

@Client.on_message(filters.command("broadcast") & is_owner)
async def broadcast_msg(client, message):
    if not message.reply_to_message:
        return await message.reply_text("📢 **Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɪᴛ.**")

    all_users = await users.find({}, {"_id": 1}).to_list(length=None)
    total_users = len(all_users)
    
    status_msg = await message.reply_text(f"🚀 **Bʀᴏᴀᴅᴄᴀsᴛ Sᴛᴀʀᴛᴇᴅ...**\nTarget: `{total_users}` users.")

    done = 0
    blocked = 0
    deleted = 0
    failed = 0

    for user in all_users:
        user_id = user["_id"]
        try:
            # Copy the replied message to the user
            await message.reply_to_message.copy(chat_id=user_id)
            done += 1
        except FloodWait as e:
            # If Telegram rate limits you, wait the required time
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(chat_id=user_id)
            done += 1
        except UserIsBlocked:
            blocked += 1
        except InputUserDeactivated:
            deleted += 1
        except Exception:
            failed += 1
        
        # Update status every 20 users to avoid spamming the log
        if done % 20 == 0:
            try:
                await status_msg.edit_text(f"🚀 **Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ...**\n\n✅ Sᴇɴᴛ: `{done}`\n🚫 Bʟᴏᴄᴋᴇᴅ: `{blocked}`\n❌ Fᴀɪʟᴇᴅ: `{failed}`")
            except:
                pass

    await status_msg.edit_text(
        f"✅ **Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!**\n\n"
        f"👤 **Tᴏᴛᴀʟ Usᴇʀs:** `{total_users}`\n"
        f"✨ **Sᴜᴄᴄᴇss:** `{done}`\n"
        f"🚫 **Bʟᴏᴄᴋᴇᴅ:** `{blocked}`\n"
        f"💀 **Dᴇʟᴇᴛᴇᴅ:** `{deleted}`\n"
        f"🛠️ **Fᴀɪʟᴇᴅ:** `{failed}`"
    )