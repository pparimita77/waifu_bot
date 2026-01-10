from pyrogram import Client, filters
from database import claims
import datetime

@Client.on_message(filters.command("gift"))
async def gift_waifu(client, message):
    # 1. Basic checks
    if not message.reply_to_message:
        return await message.reply_text("🎁 **Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ɢɪғᴛ ᴀ ᴄʜᴀʀᴀᴄᴛᴇʀ.**")
    
    try:
        char_id = message.text.split()[1]
    except IndexError:
        return await message.reply_text("❌ Usage: `/gift <char_id>`")

    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id
    
    if sender_id == receiver_id:
        return await message.reply_text("❌ You cannot gift to yourself!")

    # 2. Check if sender actually owns the character
    # We find one instance to ensure they have at least one
    check = await claims.find_one({"user_id": sender_id, "char_id": char_id})
    
    if not check:
        return await message.reply_text(f"❌ Yᴏᴜ ᴅᴏɴ'ᴛ ᴏᴡɴ ᴄʜᴀʀᴀᴄᴛᴇʀ ID `{char_id}`!")

    # 3. THE TRANSFER LOGIC
    # First, delete ONE instance from the sender
    delete_result = await claims.delete_one({"_id": check["_id"]})
    
    if delete_result.deleted_count > 0:
        # Second, insert a new record for the receiver
        await claims.insert_one({
            "user_id": receiver_id,
            "char_id": char_id,
            "date": datetime.datetime.now()
        })
        
        receiver_name = message.reply_to_message.from_user.first_name
        await message.reply_text(
            f"🎁 **Gɪғᴛ Sᴜᴄᴄᴇssғᴜʟ!**\n\n"
            f"👤 **Fʀᴏᴍ:** {message.from_user.mention}\n"
            f"👤 **Tᴏ:** {message.reply_to_message.from_user.mention}\n"
            f"🆔 **ID:** `{char_id}`"
        )
    else:
        await message.reply_text("❌ Transfer failed. Please try again.")