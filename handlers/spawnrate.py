from pyrogram import Client, filters
from database import settings 
from config import OWNER_ID

@Client.on_message(filters.command("spawnrate"), group=-1)
async def set_global_spawnrate(client, message):
    # STRICT OWNER ONLY
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Access Denied.**")

    if len(message.command) < 2:
        current_rate = await get_global_spawnrate()
        return await message.reply_text(
            f"📊 **Current Spawn Rate:** `{current_rate}` messages.\n"
            f"🔍 **Usage:** `/spawnrate [number]`\n"
            f"Example: `/spawnrate 50`"
        )

    try:
        new_rate = int(message.command[1])
        if new_rate < 1:
            return await message.reply_text("❌ Rate must be at least 1.")

        # Save to the shared global document
        await settings.update_one(
            {"_id": "global_spawn_settings"},
            {"$set": {"spawn_threshold": new_rate}},
            upsert=True
        )

        await message.reply_text(f"🚀 **Global Spawn Rate Updated!**\nCharacters will now spawn every `{new_rate}` messages in all groups.")

    except ValueError:
        await message.reply_text("❌ Please provide a valid number.")

async def get_global_spawnrate():
    """Fetches the current global rate from DB"""
    data = await settings.find_one({"_id": "global_spawn_settings"})
    if not data or "spawn_threshold" not in data:
        return 100  # Standard default
    return data["spawn_threshold"]