from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users, claims, db
from datetime import datetime

@Client.on_message(filters.command("grab"))
async def grab_character(client, message):
    chat_id = int(message.chat.id)
    user_id = message.from_user.id
    
    # 1. Fetch the spawned character from the database
    spawned = await db.spawned_waifus.find_one({"chat_id": chat_id})
    
    if not spawned:
        return await message.reply_text("❌ <b>Nᴏ ᴄʜᴀʀᴀᴄᴛᴇʀ ʜᴀs sᴘᴀᴡɴᴇᴅ ʏᴇᴛ!</b>")

    # 2. Validate User Input (Name check)
    if len(message.command) < 2:
        return await message.reply_text("<b>Pʟᴇᴀsᴇ Pʀᴏᴠɪᴅᴇ A Nᴀᴍᴇ.</b>\nExample: <code>/grab Tanjiro</code>")

    user_input = " ".join(message.command[1:]).lower().strip()
    real_name = spawned['name'].lower()
    name_parts = [part.strip() for part in real_name.split()]

    # Check if input matches full name or any part of the name
    if user_input == real_name or user_input in name_parts:
        
        # 3. ATOMIC OPERATION: Use find_one_and_delete to prevent double-grabs
        deleted_spawn = await db.spawned_waifus.find_one_and_delete(
            {"chat_id": chat_id, "char_id": spawned['char_id']}
        )

        if not deleted_spawn:
            # This happens if someone else grabbed the character a millisecond earlier
            return await message.reply_text("🕒 <b>Sᴏᴏ ᴄʟᴏsᴇ! Sᴏᴍᴇᴏɴᴇ ᴇʟsᴇ ᴊᴜsᴛ ɢʀᴀʙʙᴇᴅ ʜᴇʀ!</b>")

        # 4. Save the character to the user's collection (claims)
        try:
            await claims.insert_one({
                "user_id": user_id,
                "char_id": spawned['char_id'],
                "name": spawned['name'],
                "rarity": spawned['rarity'],
                "anime": spawned.get('anime', 'Unknown'),
                "date": datetime.now()
            })
        except Exception as e:
            print(f"Database Error: {e}")
            return await message.reply_text("⚠️ <b>Eʀʀᴏʀ sᴀᴠɪɴɢ ᴛᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ.</b>")

        # 5. SUCCESS MESSAGE (Normal Form)
        success_msg = (
            "<b>Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs 🥳</b>\n\n"
            "🌊 <b>Yᴏᴜʀ Tɪᴍɪɴɢ Wᴀs Pᴇʀғᴇᴄᴛ.</b>\n"
            "<b>Tʜᴇ Gʀᴀʙ Wᴀs Sᴜᴄᴄᴇssғᴜʟ 💙</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <b>Nᴀᴍᴇ:</b> {spawned['name']}\n"
            f"🆔 <b>Iᴅ:</b> <code>{spawned['char_id']}</code>\n"
            f"🌸 <b>Rᴀʀɪᴛʏ:</b> {spawned['rarity']}\n"
            f"🎌 <b>Sᴏᴜʀᴄᴇ:</b> {spawned.get('anime', 'Unknown')}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Oᴡɴᴇʀ:</b> {message.from_user.mention}"
        )

        # Create Harem Button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎒 Vɪᴇᴡ Hᴀʀᴇᴍ", callback_data=f"harem_{user_id}")]
        ])
        
        await message.reply_text(success_msg, reply_markup=keyboard)
        
    else:
        # 6. WRONG NAME MESSAGE
        await message.reply_text("❌ <b>Wʀᴏɴɢ Nᴀᴍᴇ! Tʀʏ ᴀɢᴀɪɴ.</b>")