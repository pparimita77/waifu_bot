from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from database import users

# Simple function to remove symbols that break Telegram formatting
def safe_name(name):
    return str(name).replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")

@Client.on_message(filters.command("pay") & filters.group)
async def pay_command(client, message):
    if not message.from_user:
        return

    # 1. Parsing Input
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        try:
            amount = float(message.command[1])
        except (ValueError, IndexError):
            return await message.reply_text("❌ **Usage:** Reply to a user with `/pay [amount]`")
    else:
        if len(message.command) < 3:
            return await message.reply_text("❌ **Usage:** `/pay [user_id] [amount]`")
        try:
            target_id = int(message.command[1])
            amount = float(message.command[2])
            target_user = await client.get_users(target_id)
        except Exception:
            return await message.reply_text("❌ User not found.")

    if target_user.id == message.from_user.id:
        return await message.reply_text("⚠️ You cannot pay yourself.")
    if amount <= 0:
        return await message.reply_text("⚠️ Amount must be positive.")

    sender_id = message.from_user.id
    target_id = target_user.id
    
    s_name = safe_name(message.from_user.first_name)
    t_name = safe_name(target_user.first_name)

    text = (
        f"💸 **Pᴀʏᴍᴇɴᴛ Rᴇǫᴜᴇsᴛ**\n\n"
        f"👤 **Fʀᴏᴍ:** {s_name}\n"
        f"👤 **Tᴏ:** {t_name}\n"
        f"💰 **Aᴍᴏᴜɴᴛ:** `🌟 {amount:,.2f} Sᴛᴀʀᴅᴜsᴛ`\n\n"
        f"**Nᴏᴛᴇ:** Only {s_name} can confirm."
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Cᴏɴғɪʀᴍ Sᴛᴀʀᴅᴜsᴛ", callback_data=f"p_s_{sender_id}_{target_id}_{amount}")
        ],
        [InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data=f"p_c_{sender_id}")]
    ]

    await message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex(r"^p_"))
async def pay_callback(client, query):
    data = query.data.split("_")
    action = data[1] # 's' for stardust, 'c' for cancel
    allowed_sender_id = int(data[2])

    if query.from_user.id != allowed_sender_id:
        return await query.answer("❌ This is not your transaction!", show_alert=True)

    if action == "c":
        await query.message.edit_text("❌ Payment Cancelled by the sender.")
        return

    currency = "stardust"
    target_id = int(data[3])
    amount = float(data[4])

    # Fetch sender data using $or to find them regardless of key format
    sender_data = await users.find_one({"$or": [{"user_id": allowed_sender_id}, {"_id": allowed_sender_id}]}) or {}
    
    try:
        current_balance = float(sender_data.get(currency, 0))
    except:
        current_balance = 0.0

    if current_balance < amount:
        return await query.answer(f"❌ You don't have enough Stardust!", show_alert=True)

    # 🛠️ UNIVERSAL UPDATE: We use update_one with $or to ensure we hit the right record
    # Deduct from Sender
    await users.update_one(
        {"$or": [{"user_id": allowed_sender_id}, {"_id": allowed_sender_id}]},
        {"$inc": {currency: -amount}}
    )
    # Add to Target (Using upsert=True in case recipient is a new user)
    await users.update_one(
        {"$or": [{"user_id": target_id}, {"_id": target_id}]},
        {"$inc": {currency: amount}},
        upsert=True
    )

    await query.message.edit_text(
        f"✅ **Pᴀʏᴍᴇɴᴛ Sᴜᴄᴄᴇssғᴜʟ**\n\n"
        f"Sᴇɴᴛ `🌟 {amount:,.2f}` Sᴛᴀʀᴅᴜsᴛ to the recipient.",
        parse_mode=ParseMode.MARKDOWN
    )