import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import users
from config import OWNER_ID

# Ensure OWNER_ID is always a flat list of integers
OWNERS = OWNER_ID if isinstance(OWNER_ID, list) else [OWNER_ID]

@Client.on_message(filters.command("add_bal") & filters.user(OWNERS))
async def add_balance_cmd(client, message):
    if len(message.command) < 4:
        return await message.reply_text(
            "💰 <b>Usᴀɢᴇ:</b>\n"
            "<code>/add_bal [user_id or all] [emerald or stardust] [amount]</code>",
            parse_mode=ParseMode.HTML
        )

    target = message.command[1].lower()
    currency = message.command[2].lower()
    
    try:
        amount = float(message.command[3])
    except ValueError:
        return await message.reply_text("❌ <b>Amount must be a number!</b>", parse_mode=ParseMode.HTML)

    # Determine database field
    if currency in ["emerald", "emeralds"]:
        field = "emeralds"
        amount = int(amount) # Usually whole numbers for emeralds
    elif currency in ["stardust", "dust"]:
        field = "stardust"
    else:
        return await message.reply_text("❌ <b>Invalid currency!</b> Use <code>emerald</code> or <code>stardust</code>.", parse_mode=ParseMode.HTML)

    

    if target == "all":
        # Global update using $inc (increment)
        await users.update_many({}, {"$inc": {field: amount}})
        text = f"✅ <b>GLOBAL UPDATE:</b> Added <code>{amount}</code> {field} to everyone."
    
    elif target.isdigit():
        target_id = int(target)
        # Update specific user by matching _id or user_id
        result = await users.update_one(
            {"$or": [{"_id": target_id}, {"user_id": target_id}]},
            {"$inc": {field: amount}}
        )
        
        if result.matched_count > 0:
            text = f"✅ <b>SUCCESS:</b> Added <code>{amount}</code> {field} to user <code>{target_id}</code>."
        else:
            text = f"❌ <b>User <code>{target_id}</code> not found in database.</b>"
    else:
        text = "❌ <b>Invalid target!</b> Provide a User ID or type <code>all</code>."

    await message.reply_text(text, parse_mode=ParseMode.HTML)