from pyrogram import Client, filters
from database import users

@Client.on_message(filters.command("convert"))
async def convert_gems_to_stardust(client, message):
    user_id = message.from_user.id
    
    # Usage: /convert <amount_of_gems_to_spend>
    if len(message.command) < 2:
        return await message.reply_text(
            "🔄 **Gᴇᴍs ᴛᴏ Sᴛᴀʀᴅᴜsᴛ Cᴏɴᴠᴇʀᴛᴇʀ**\n\n"
            "**Rate:** 100 💎 Gᴇᴍs = 1 🌟 Sᴛᴀʀᴅᴜsᴛ\n"
            "**Usage:** `/convert <gems_amount>`\n"
            "**Example:** `/convert 150` (Gives 1.5 Stardust)"
        )

    try:
        gems_to_spend = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Please enter a valid number of Gems.")

    if gems_to_spend <= 0:
        return await message.reply_text("❌ Amount must be greater than 0.")

    # Fetch user data
    user_data = await users.find_one({"_id": user_id}) or {}
    user_gems = user_data.get("gems", 0)

    # Check if user has enough gems
    if user_gems < gems_to_spend:
        return await message.reply_text(
            f"❌ **Insufficient Gems!**\n\n"
            f"You tried to spend: 💎 `{gems_to_spend:,}`\n"
            f"You only have: 💎 `{user_gems:,}`"
        )

    # Calculation: Gems / 100 = Stardust (Decimal allowed)
    stardust_received = float(gems_to_spend / 100)

    # Update Database
    await users.update_one(
        {"_id": user_id},
        {
            "$inc": {
                "gems": -gems_to_spend,        # Subtract integer gems
                "stardust": stardust_received  # Add decimal stardust
            }
        }
    )

    await message.reply_text(
        f"✅ **Cᴏɴᴠᴇʀsɪᴏɴ Cᴏᴍᴘʟᴇᴛᴇ!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 **Spent:** 💎 `{gems_to_spend:,}` Gems\n"
        f"📥 **Received:** 🌟 `{stardust_received:.2f}` Stardust\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )