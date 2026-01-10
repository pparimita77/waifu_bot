from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users

@Client.on_message(filters.command("pay"))
async def pay_initial(client, message):
    # 1. Validation: Must reply to a user or provide an ID
    if not message.reply_to_message and len(message.command) < 3:
        return await message.reply_text(
            "📝 **Usage:**\nReply to someone with `/pay <amount>`\n"
            "Or use `/pay <user_id> <amount>`"
        )

    # 2. Extract Target User and Amount
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        amount_idx = 1
    else:
        try:
            target_id = int(message.command[1])
            target_user = await client.get_users(target_id)
            amount_idx = 2
        except Exception:
            return await message.reply_text("❌ Invalid User ID.")

    try:
        amount = int(message.command[amount_idx])
    except (ValueError, IndexError):
        return await message.reply_text("❌ Please enter a valid numerical amount.")

    if amount <= 0:
        return await message.reply_text("❌ Amount must be greater than 0.")

    if target_user.id == message.from_user.id:
        return await message.reply_text("⚠️ You cannot pay yourself!")

    # 3. Currency Selection Buttons
    text = (
        f"💸 **Pᴀʏᴍᴇɴᴛ Pᴇɴᴅɪɴɢ**\n\n"
        f"👤 **To:** {target_user.mention}\n"
        f"💰 **Amount:** `{amount:,}`\n\n"
        f"Select the currency you wish to send:"
    )

    buttons = [[
        InlineKeyboardButton("💎 Gᴇᴍs", callback_data=f"pay_gems_{target_user.id}_{amount}"),
        InlineKeyboardButton("🌟 Sᴛᴀʀᴅᴜsᴛ", callback_data=f"pay_stardust_{target_user.id}_{amount}")
    ]]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^pay_"))
async def process_payment(client, query):
    sender_id = query.from_user.id
    data = query.data.split("_")
    
    currency = data[1] # 'gems' or 'stardust'
    target_id = int(data[2])
    amount = int(data[3])

    # 1. Check Sender's Balance
    sender_data = await users.find_one({"_id": sender_id}) or {}
    sender_bal = sender_data.get(currency, 0)

    if sender_bal < amount:
        emoji = "💎" if currency == "gems" else "🌟"
        return await query.answer(f"❌ You don't have enough {emoji}!", show_alert=True)

    # 2. Perform Transaction (Atomic Update)
    # Deduct from sender
    await users.update_one({"_id": sender_id}, {"$inc": {currency: -amount}})
    # Add to receiver
    await users.update_one({"_id": target_id}, {"$inc": {currency: amount}}, upsert=True)

    # 3. Notify
    emoji = "💎" if currency == "gems" else "🌟"
    target_user = await client.get_users(target_id)
    
    success_text = (
        f"✅ **Pᴀʏᴍᴇɴᴛ Sᴜᴄᴄᴇssғᴜʟ!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 **From:** {query.from_user.mention}\n"
        f"📥 **To:** {target_user.mention}\n"
        f"💰 **Sent:** {amount:,} {emoji} {currency.capitalize()}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    await query.message.edit_text(success_text)
    
    # Optional: Alert the receiver
    try:
        await client.send_message(target_id, f"🎁 {query.from_user.mention} sent you **{amount:,} {emoji} {currency.capitalize()}**!")
    except:
        pass