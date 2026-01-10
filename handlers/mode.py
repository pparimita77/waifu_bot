from pyrogram import Client, filters
from config import OWNER_ID, DEVS
from database import settings

@Client.on_message(filters.command("mode") & filters.user([OWNER_ID] + DEVS))
async def switch_mode(client, message):
    # Get current status (default to False if not set)
    current_mode = await settings.find_one({"_id": "maintenance_mode"})
    is_maintenance = current_mode.get("status", False) if current_mode else False

    # Toggle the status
    new_status = not is_maintenance
    await settings.update_one(
        {"_id": "maintenance_mode"},
        {"$set": {"status": new_status}},
        upsert=True
    )

    status_text = "⚠️ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ: ON**" if new_status else "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ: OFF**"
    await message.reply_text(f"🌊 {status_text}\n\n{'Users cannot use commands.' if new_status else 'Everyone can use the bot now.'}")

# Middleware to block users during maintenance
@Client.on_message(~filters.user([OWNER_ID] + DEVS), group=-1)
async def check_maintenance(client, message):
    mode = await settings.find_one({"_id": "maintenance_mode"})
    if mode and mode.get("status", False):
        # We don't reply to every message to avoid spam, just stop the execution
        message.stop_propagation()