from pyrogram import Client, filters
from database import users, characters, claims
from sudo import is_dev # Using the filter that includes Owner + Devs

@Client.on_message(filters.command("stats") & is_dev)
async def get_bot_stats(client, message):
    # Send a "Loading" message because counting large databases can take a second
    status_msg = await message.reply_text("📊 **Fᴇᴛᴄʜɪɴɢ Dᴀᴛᴀʙᴀsᴇ Sᴛᴀᴛɪsᴛɪᴄs...**")

    try:
        # Count total documents in each collection
        total_users = await users.count_documents({})
        total_waifus = await characters.count_documents({})
        total_claims = await claims.count_documents({})

        # Optional: Count how many users have Premium
        premium_users = await users.count_documents({"is_premium": True})

        stats_text = (
            "📊 **Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ Bᴏᴛ Sᴛᴀᴛs**\n\n"
            f"👤 **Tᴏᴛᴀʟ Usᴇʀs:** `{total_users}`\n"
            f"⭐ **Pʀᴇᴍɪᴜᴍ Usᴇʀs:** `{premium_users}`\n\n"
            f"🌸 **Tᴏᴛᴀʟ Wᴀɪғᴜs (DB):** `{total_waifus}`\n"
            f"📥 **Tᴏᴛᴀʟ Cʟᴀɪᴍᴇᴅ:** `{total_claims}`\n\n"
            f"📈 **Sᴛᴀᴛᴜs:** `Oᴘᴇʀᴀᴛɪᴏɴᴀʟ`"
        )

        await status_msg.edit_text(stats_text)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Eʀʀᴏʀ:** `{str(e)}`平衡")