import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import claims, characters
from utils import is_subscribed, send_join_message

@Client.on_message(filters.command("gift"))
async def gift_waifu(client, message):
    user_id = message.from_user.id
    
    # 1. Force Join Check
    if not await is_subscribed(client, user_id):
        return await send_join_message(client, message)

    # 2. Basic checks
    if not message.reply_to_message:
        return await message.reply_text("🎁 **Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ɢɪғᴛ ᴀ ᴄʜᴀʀᴀᴄᴛᴇʀ.**")
    
    try:
        char_id = message.text.split()[1]
    except IndexError:
        return await message.reply_text("❌ Usage: `/gift <char_id>`")

    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id
    
    if sender_id == receiver_id:
        return await message.reply_text("❌ Yᴏᴜ ᴄᴀɴɴᴏᴛ ɢɪғᴛ ᴛᴏ ʏᴏᴜʀsᴇʟғ!")

    # 3. Check ownership and get character name
    check = await claims.find_one({"user_id": sender_id, "char_id": char_id})
    if not check:
        return await message.reply_text(f"❌ Yᴏᴜ ᴅᴏɴ'ᴛ ᴏᴡɴ ᴄʜᴀʀᴀᴄᴛᴇʀ ID `{char_id}`!")

    char_info = await characters.find_one({"id": char_id})
    char_name = char_info.get("name", "Unknown") if char_info else "Unknown"

    # 4. Confirmation Menu
    receiver_name = message.reply_to_message.from_user.first_name
    text = (
        f"🎁 **Gɪғᴛ Cᴏɴғɪʀᴍᴀᴛɪᴏɴ**\n\n"
        f"Yᴏᴜ ᴀʀᴇ ᴀʙᴏᴜᴛ ᴛᴏ ɢɪғᴛ **{char_name}** ({char_id}) ᴛᴏ **{receiver_name}**.\n\n"
        f"⚠️ *Tʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!*"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Cᴏɴғɪʀᴍ", callback_data=f"gift_yes_{char_id}_{receiver_id}_{sender_id}"),
            InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data=f"gift_no_{sender_id}")
        ]
    ])

    await message.reply_text(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("^gift_"))
async def handle_gift_callback(client, callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    action = data[1]
    
    # gift_yes_{char_id}_{receiver_id}_{sender_id}
    # gift_no_{sender_id}
    
    sender_id = int(data[-1])
    
    # Only the sender can click the buttons
    if callback_query.from_user.id != sender_id:
        return await callback_query.answer("❌ This menu is not for you!", show_alert=True)

    if action == "no":
        return await callback_query.message.edit_text("❌ **Gɪғᴛ Cᴀɴᴄᴇʟʟᴇᴅ.**")

    # If action is "yes"
    char_id = data[2]
    receiver_id = int(data[3])

    # Re-verify ownership at time of click
    check = await claims.find_one({"user_id": sender_id, "char_id": char_id})
    if not check:
        return await callback_query.message.edit_text("❌ Yᴏᴜ ɴᴏ ʟᴏɴɢᴇʀ ᴏᴡɴ ᴛʜɪs ᴄʜᴀʀᴀᴄᴛᴇʀ!")

    # TRANSFER LOGIC
    delete_result = await claims.delete_one({"_id": check["_id"]})
    if delete_result.deleted_count > 0:
        await claims.insert_one({
            "user_id": receiver_id,
            "char_id": char_id,
            "date": datetime.datetime.now()
        })
        
        # Get names for final message
        receiver_user = await client.get_users(receiver_id)
        
        await callback_query.message.edit_text(
            f"🎁 **Gɪғᴛ Sᴜᴄᴄᴇssғᴜʟ!**\n\n"
            f"👤 **Fʀᴏᴍ:** {callback_query.from_user.mention}\n"
            f"👤 **Tᴏ:** {receiver_user.mention}\n"
            f"🆔 **ID:** `{char_id}`\n\n"
            f"✨ *Tʜᴇ ᴄʜᴀʀᴀᴄᴛᴇʀ ʜᴀs ʙᴇᴇɴ ᴛʀᴀɴsғᴇʀʀᴇᴅ.*"
        )
    else:
        await callback_query.answer("❌ Transfer failed.", show_alert=True)