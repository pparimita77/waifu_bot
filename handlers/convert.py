from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import users

# Conversion Rate: 100 Stardust = 1 Emerald
RATE = 100

@Client.on_message(filters.command("convert") & filters.group)
async def convert_currency(client, message):
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        return await message.reply_text(
            "🔄 <b>Cᴜʀʀᴇɴᴄʏ Cᴏɴᴠᴇʀᴛᴇʀ</b>\n\n"
            "<b>Rate:</b>\n"
            "• 🌟 100 Stardust ➔ 💠 1 Emerald Point\n\n"
            "<b>Usage:</b>\n"
            "• <code>/convert 500</code>\n\n"
            "<i>Note: Conversion is permanent.</i>",
            parse_mode=ParseMode.HTML
        )

    try:
        stardust_to_spend = float(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Please enter a valid numerical amount.")

    if stardust_to_spend <= 0:
        return await message.reply_text("❌ Amount must be greater than 0.")

    # Fetch user data - checking both _id and user_id formats
    user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]}) or {}

    try:
        user_dust = float(user_data.get("stardust", 0))
    except (ValueError, TypeError):
        user_dust = 0.0

    if user_dust < stardust_to_spend:
        return await message.reply_text(
            f"❌ <b>Insufficient Stardust!</b>\n"
            f"You have: 🌟 <code>{user_dust:.2f}</code>\n"
            f"You need: 🌟 <code>{stardust_to_spend:.2f}</code>",
            parse_mode=ParseMode.HTML
        )

    # Calculation
    emerald_received = round(stardust_to_spend / RATE, 2)
    
    # Update Database
    update = {
        "$inc": {
            "stardust": -stardust_to_spend,
            "emeralds": emerald_received 
        }
    }

    await users.update_one(
        {"$or": [{"user_id": user_id}, {"_id": user_id}]},
        update,
        upsert=True
    )

    await message.reply_text(
        f"✅ <b>Cᴏɴᴠᴇʀsɪᴏɴ Cᴏᴍᴘʟᴇᴛᴇ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 <b>Spent:</b> 🌟 <code>{stardust_to_spend:.2f}</code> Stardust\n"
        f"📥 <b>Received:</b> 💠 <code>{emerald_received:.2f}</code> Emeralds\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        parse_mode=ParseMode.HTML
    )