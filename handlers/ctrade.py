import html
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import claims, characters

# Temporary storage for active trade requests
pending_trades = {}

# ONLY triggers for specific trade actions, ignoring shop clicks
@Client.on_callback_query(filters.regex(r"^(trade_accept_|trade_decline_)"))
async def trade_callback(client, query: CallbackQuery):
    if not message.reply_to_message:
        return await message.reply_text("❌ <b>Reply to the user you want to trade with!</b>")

    if len(message.command) < 3:
        return await message.reply_text("📝 <b>Usage:</b> <code>/ctrade <your_id> <their_id></code>")

    sender_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id
    give_id = str(message.command[1])
    take_id = str(message.command[2])

    if sender_id == target_id:
        return await message.reply_text("❌ <b>You cannot trade with yourself!</b>")

    # 1. Verify Ownership
    own_check = await claims.find_one({"user_id": sender_id, "char_id": give_id})
    target_own_check = await claims.find_one({"user_id": target_id, "char_id": take_id})

    if not own_check:
        return await message.reply_text(f"❌ <b>You don't own ID:</b> <code>{give_id}</code>")
    if not target_own_check:
        return await message.reply_text(f"❌ <b>They don't own ID:</b> <code>{take_id}</code>")

    char1 = await characters.find_one({"id": give_id})
    char2 = await characters.find_one({"id": take_id})
    
    give_name = char1['name'] if char1 else "Unknown"
    take_name = char2['name'] if char2 else "Unknown"

    # 2. Store Trade Data (Keyed by target_id so we know who must click)
    pending_trades[target_id] = {
        "sender": sender_id,
        "give": give_id,
        "take": take_id,
        "give_name": give_name,
        "take_name": take_name
    }

    # BUTTONS: Format is tr_action_targetID
    # We use 'tr' to match your regex and 'acc'/'dec' for action
    buttons = [
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"tr_acc_{target_id}"),
            InlineKeyboardButton("❌ Decline", callback_data=f"tr_dec_{target_id}")
        ]
    ]

    sender_link = f"<a href='tg://user?id={sender_id}'>{html.escape(message.from_user.first_name)}</a>"
    target_first_name = html.escape(message.reply_to_message.from_user.first_name)

    await message.reply_text(
        f"🤝 <b>Tʀᴀᴅᴇ Rᴇǫᴜᴇsᴛ</b>\n\n"
        f"👤 <b>Fʀᴏᴍ:</b> {sender_link}\n"
        f"🎁 <b>Gɪᴠɪɴɢ:</b> {html.escape(give_name)} (<code>{give_id}</code>)\n"
        f"📥 <b>Tᴀᴋɪɴɢ:</b> {html.escape(take_name)} (<code>{take_id}</code>)\n\n"
        f"<b>{target_first_name}, do you accept this trade?</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^tr_"))
async def trade_callback(client, query: CallbackQuery):
    data = query.data.split("_")
    
    # Safety Check: tr (0), action (1), target_id (2)
    if len(data) < 3:
        return await query.answer("❌ Invalid Trade Data.")

    action = data[1]
    target_id = int(data[2])

    # 3. Security Check: Only the receiver can click
    if query.from_user.id != target_id:
        return await query.answer("❌ This trade request is not for you!", show_alert=True)

    trade = pending_trades.get(target_id)
    if not trade:
        return await query.message.edit_text("❌ <b>Trade expired or already processed.</b>")

    if action == "acc":
        # Final Ownership Check
        s_check = await claims.find_one({"user_id": trade['sender'], "char_id": trade['give']})
        t_check = await claims.find_one({"user_id": target_id, "char_id": trade['take']})

        if not s_check or not t_check:
            pending_trades.pop(target_id, None)
            return await query.message.edit_text("❌ <b>Trade failed:</b> Items are no longer with original owners.")

        # Swap Ownership
        await claims.update_one({"_id": s_check['_id']}, {"$set": {"user_id": target_id}})
        await claims.update_one({"_id": t_check['_id']}, {"$set": {"user_id": trade['sender']}})

        await query.message.edit_text(
            f"✅ <b>Tʀᴀᴅᴇ Sᴜᴄᴄᴇssғᴜʟ!</b>\n\n"
            f"♻️ <b>{html.escape(trade['give_name'])}</b> and <b>{html.escape(trade['take_name'])}</b> have been swapped!"
        )
    else:
        await query.message.edit_text("❌ <b>Trade declined.</b>")

    # Clear memory
    pending_trades.pop(target_id, None)