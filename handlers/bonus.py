import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ParseMode
from database import users 

# --- CONFIGURATION ---
AUTH_CHANNEL = "@Tomioka_Supportcore" 

async def is_subscribed(client, user_id):
    try:
        member = await client.get_chat_member(AUTH_CHANNEL, user_id)
        if member.status in ["kicked", "left"]:
            return False
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Force Join Error: {e}")
        return True

def get_bonus_buttons(user_data, user_id):
    now = datetime.now()
    
    last_daily = user_data.get("last_daily")
    daily_claimed = last_daily and (now - last_daily) < timedelta(days=1)
    daily_text = "✨ Dᴀɪʟʏ (10,000 Sᴛᴀʀᴅᴜsᴛ) ✅" if daily_claimed else "✨ Dᴀɪʟʏ (10,000 Sᴛᴀʀᴅᴜsᴛ)"
    
    last_weekly = user_data.get("last_weekly")
    weekly_claimed = last_weekly and (now - last_weekly) < timedelta(days=7)
    weekly_text = "💎 Wᴇᴇᴋʟʏ (100,000 Sᴛᴀʀᴅᴜsᴛ) ✅" if weekly_claimed else "💎 Wᴇᴇᴋʟʏ (100,000 Sᴛᴀʀᴅᴜsᴛ)"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(daily_text, callback_data=f"claim_daily_{user_id}")],
        [InlineKeyboardButton(weekly_text, callback_data=f"claim_weekly_{user_id}")]
    ])

@Client.on_message(filters.command("bonus"), group=0)
async def bonus_menu(client, message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    if not await is_subscribed(client, user_id):
        channel_username = AUTH_CHANNEL.replace("@", "")
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Jᴏɪɴ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ", url=f"https://t.me/{channel_username}")],
            [InlineKeyboardButton("🔄 Cʜᴇᴄᴋ Aɢᴀɪɴ", callback_data=f"check_sub_{user_id}")]
        ])
        return await message.reply_text(
            "❌ <b>Aᴄᴄᴇss Dᴇɴɪᴇᴅ!</b>\n\n"
            "Yᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ᴛᴏ ᴄʟᴀɪᴍ ʙᴏɴᴜsᴇs.",
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )

    user_data = await users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}]}) or {}

    now = datetime.now()
    streak = user_data.get("streak", 0)
    high_streak = user_data.get("high_streak", 0)
    last_daily = user_data.get("last_daily")

    if last_daily and isinstance(last_daily, datetime):
        if (now - last_daily) > timedelta(hours=48):
            streak = 0
            await users.update_one(
                {"$or": [{"user_id": user_id}, {"_id": user_id}]},
                {"$set": {"streak": 0}}
            )

    day_name = now.strftime("%A")
    week_no = now.isocalendar()[1]

    # Removed all ** from the text below
    text = (
        f"⛩️ Oʜᴀʏᴏ, {name}-Sᴀɴ! 💫\n\n"
        f"🌸 Dᴀʏ : `{day_name}`\n"
        f"🎐 Wᴇᴇᴋ : `{week_no}`\n\n"
        f"🎗️ Cᴜʀʀᴇɴᴛ Sᴛʀᴇᴀᴋ : `{streak}` Dᴀʏs\n"
        f"🏆 Hɪɢʜᴇsᴛ Sᴛʀᴇᴀᴋ : `{high_streak}` Dᴀʏs\n\n"
        f"🥂 Cʟᴀɪᴍ Yᴏᴜʀ Bᴏɴᴜs Rᴇᴡᴀʀᴅs 🥂"
    )

    await message.reply_text(text, reply_markup=get_bonus_buttons(user_data, user_id))

@Client.on_callback_query(filters.regex("^(claim_|check_sub_)"))
async def handle_bonus_callbacks(client, callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    
    if data[0] == "check":
        if await is_subscribed(client, callback_query.from_user.id):
            await callback_query.answer("✅ Subscribed! You can now use /bonus.", show_alert=True)
            return await callback_query.message.delete()
        else:
            return await callback_query.answer("❌ You still haven't joined!", show_alert=True)

    action = data[1] 
    owner_id = int(data[2])
    clicker_id = callback_query.from_user.id
    
    if clicker_id != owner_id:
        return await callback_query.answer("❌ This menu is not for you!", show_alert=True)

    if not await is_subscribed(client, clicker_id):
        return await callback_query.answer("❌ You left the support group! Rejoin to claim.", show_alert=True)

    now = datetime.now()
    user_data = await users.find_one({"$or": [{"user_id": owner_id}, {"_id": owner_id}]}) or {}

    last_key = f"last_{action}"
    reward = 10000.0 if action == "daily" else 100000.0
    cooldown = timedelta(days=1) if action == "daily" else timedelta(days=7)

    last_claim = user_data.get(last_key)
    if last_claim and isinstance(last_claim, datetime):
        if (now - last_claim) < cooldown:
            remaining = cooldown - (now - last_claim)
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            return await callback_query.answer(f"⏳ Already Claimed! Wait {hours}h {minutes}m.", show_alert=True)

    update_ops = {"$inc": {"stardust": float(reward)}, "$set": {last_key: now}}

    if action == "daily":
        new_streak = user_data.get("streak", 0) + 1
        update_ops["$set"]["streak"] = new_streak
        if new_streak > user_data.get("high_streak", 0):
            update_ops["$set"]["high_streak"] = new_streak

    await users.update_one({"$or": [{"user_id": owner_id}, {"_id": owner_id}]}, update_ops, upsert=True)
    
    updated_user_data = await users.find_one({"$or": [{"user_id": owner_id}, {"_id": owner_id}]})

    await callback_query.answer(f"✅ {action.title()} bonus added!")
    
    await callback_query.message.edit_reply_markup(
        reply_markup=get_bonus_buttons(updated_user_data, owner_id)
    )
    
    # Removed ** from the broadcast message below
    await client.send_message(
        callback_query.message.chat.id,
        f"✨ {callback_query.from_user.mention} claimed their {action.upper()} bonus of `{reward:,.0f}` Stardust!"
    )