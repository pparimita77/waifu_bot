from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import users
import datetime

@Client.on_message(filters.command("bonus"))
async def bonus_menu(client, message):
    keyboard = [
        [InlineKeyboardButton("Daily Bonus : 100 Gems", callback_data="claim_daily")],
        [InlineKeyboardButton("Weekly Bonus : 1000 Gems", callback_data="claim_weekly")]
    ]
    
    await message.reply_text(
        "🎁 **Tᴏᴍɪᴏᴋᴀ Gɪʏᴜ Bᴏɴᴜs Mᴇɴᴜ**\n\nCʟᴀɪᴍ ʏᴏᴜʀ ʀᴇᴡᴀʀᴅs ʙᴇʟᴏᴡ:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex(r"claim_(daily|weekly)"))
async def bonus_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Setup logic based on which button was clicked
    if data == "claim_daily":
        amount = 100
        db_field = "last_daily_date"
        reward_name = "Daily"
        # Check for 1 day
        check_date = datetime.date.today()
    else:
        amount = 1000
        db_field = "last_weekly_date"
        reward_name = "Weekly"
        # Check for 7 days
        check_date = datetime.date.today()

    # 1. Check Database
    user_data = await users.find_one({"_id": user_id})
    last_claim_str = user_data.get(db_field) if user_data else None
    
    today = datetime.date.today()
    
    if last_claim_str:
        last_claim_date = datetime.date.fromisoformat(last_claim_str)
        delta = today - last_claim_date
        
        # Validation for Daily (1 day) vs Weekly (7 days)
        if data == "claim_daily" and delta.days < 1:
            return await callback_query.answer("❌ Cᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ!", show_alert=True)
        if data == "claim_weekly" and delta.days < 7:
            return await callback_query.answer(f"❌ Cᴏᴍᴇ ʙᴀᴄᴋ ɪɴ {7 - delta.days} ᴅᴀʏs!", show_alert=True)

    # 2. Add Gems and Update Date
    await users.update_one(
        {"_id": user_id},
        {
            "$inc": {"gems": amount}, 
            "$set": {db_field: today.isoformat()}
        },
        upsert=True
    )

    # 3. Update UI to show checkmark ✅
    # We update the specific button that was clicked
    current_keyboard = callback_query.message.reply_markup.inline_keyboard
    new_keyboard = []
    
    for row in current_keyboard:
        new_row = []
        for btn in row:
            if btn.callback_data == data:
                new_row.append(InlineKeyboardButton(f"{reward_name} Cʟᴀɪᴍᴇᴅ ✅", callback_data="done"))
            else:
                new_row.append(btn)
        new_keyboard.append(new_row)

    await callback_query.edit_message_text(
        f"✅ **{reward_name} Bᴏɴᴜs Cʟᴀɪᴍᴇᴅ!**\n\n+{amount} Gᴇᴍs ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ.",
        reply_markup=InlineKeyboardMarkup(new_keyboard)
    )
    await callback_query.answer(f"Success! +{amount} Gems")
    
    buttons = [
        [InlineKeyboardButton("Daily Bonus : 100 Gems", callback_data="claim_daily")],
        [InlineKeyboardButton("Weekly Bonus : 1000 Gems", callback_data="claim_weekly")]
    ]
    
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))