from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import claims

# Temporary storage for active trade requests
# Structure: {target_user_id: {"sender": sender_id, "give": char_id, "take": char_id}}
pending_trades = {}

@Client.on_message(filters.command("trade") & filters.group)
async def trade_command(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to the user you want to trade with!")

    if len(message.command) < 3:
        return await message.reply_text("📝 **Usage:** `/trade <your_char_id> <their_char_id>`")

    sender_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id
    give_id = message.command[1]
    take_id = message.command[2]

    if sender_id == target_id:
        return await message.reply_text("❌ You can't trade with yourself!")

    # Verify Sender owns the character
    own_check = await claims.find_one({"user_id": sender_id, "char_id": give_id})
    if not own_check:
        return await message.reply_text(f"❌ You don't own character ID: {give_id}")

    # Verify Target owns the character
    target_check = await claims.find_one({"user_id": target_id, "char_id": take_id})
    if not target_check:
        return await message.reply_text(f"❌ They don't own character ID: {take_id}")

    # Save to pending trades
    pending_trades[target_id] = {
        "sender": sender_id,
        "give": give_id,
        "take": take_id,
        "give_name": own_check['name'],
        "take_name": target_check['name']
    }

    buttons = [
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"tr_acc_{target_id}"),
            InlineKeyboardButton("❌ Decline", callback_data=f"tr_dec_{target_id}")
        ]
    ]

    await message.reply_text(
        f"🤝 **Tʀᴀᴅᴇ Rᴇǫᴜᴇsᴛ**\n\n"
        f"👤 **Fʀᴏᴍ:** {message.from_user.mention}\n"
        f"🎁 **Gɪᴠɪɴɢ:** {own_check['name']} (`{give_id}`)\n"
        f"📥 **Tᴀᴋɪɴɢ:** {target_check['name']} (`{take_id}`)\n\n"
        f"**{message.reply_to_message.from_user.first_name}, do you accept?**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^tr_"))
async def trade_callback(client, query: CallbackQuery):
    data = query.data.split("_")
    action = data[1]
    target_id = int(data[2])

    if query.from_user.id != target_id:
        return await query.answer("❌ This trade is not for you!", show_alert=True)

    trade = pending_trades.get(target_id)
    if not trade:
        return await query.answer("❌ Trade expired or invalid.", show_alert=True)

    if action == "acc":
        # 1. Swap ownership in database
        # Give Sender's char to Target
        await claims.update_one(
            {"user_id": trade['sender'], "char_id": trade['give']},
            {"$set": {"user_id": target_id}}
        )
        # Give Target's char to Sender
        await claims.update_one(
            {"user_id": target_id, "char_id": trade['take']},
            {"$set": {"user_id": trade['sender']}}
        )

        await query.message.edit_text(
            f"✅ **Tʀᴀᴅᴇ Sᴜᴄᴄᴇssғᴜʟ!**\n\n"
            f"♻️ **{trade['give_name']}** and **{trade['take_name']}** have been swapped!"
        )
    else:
        await query.message.edit_text("❌ Trade declined.")

    # Clean up
    if target_id in pending_trades:
        del pending_trades[target_id]