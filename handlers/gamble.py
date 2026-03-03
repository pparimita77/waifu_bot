import random
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import users

@Client.on_message(filters.command(["gamble", "bet"]) & filters.group, group=0)
async def gamble_cmd(client, message):
    if not message.from_user:
        return

    # Check for arguments safely
    if len(message.command) < 2:
        # Use ParseMode.MARKDOWN to ensure **Usage** works
        return await message.reply_text(
            "🎲 **Usage:** `/gamble <amount>`",
            parse_mode=ParseMode.MARKDOWN
        )

    user_id = message.from_user.id
    try:
        # Handle 'all' or specific number
        if message.command[1].lower() == "all":
            user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]})
            bet_amount = float(user_data.get('stardust', 0)) if user_data else 0
        else:
            bet_amount = float(message.command[1])
    except (ValueError, IndexError):
        return await message.reply_text("❌ Please enter a valid number or `all`.")

    if bet_amount < 10:
        return await message.reply_text("⚠️ Minimum bet is `10` Stardust.")

    # 1. Fetch user data
    user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]})
    current_stardust = float(user_data.get('stardust', 0)) if user_data else 0

    if current_stardust < bet_amount:
        return await message.reply_text("❌ You don't have enough Stardust!")

    # 2. Gambling Logic
    win = random.choice([True, False])
    db_filter = {"$or": [{"user_id": user_id}, {"_id": user_id}]}

    if win:
        profit = bet_amount
        await users.update_one(db_filter, {"$inc": {"stardust": profit}})
        result_msg = f"🎊 **Yᴏᴜ Wᴏɴ!**\n💰 Pʀᴏғɪᴛ: `+{profit:,.2f}` Sᴛᴀʀᴅᴜsᴛ"
    else:
        await users.update_one(db_filter, {"$inc": {"stardust": -bet_amount}})
        result_msg = f"💀 **Yᴏᴜ Lᴏsᴛ!**\n💸 Lᴏss: `-{bet_amount:,.2f}` Sᴛᴀʀᴅᴜsᴛ"

    # 3. Final Response with mention to avoid character issues
    text = (
        f"⛩️ **Gᴀᴍʙʟᴇ Rᴇsᴜʟᴛs: {message.from_user.first_name}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{result_msg}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)