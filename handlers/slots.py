import random
import time
import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from database import users, is_user_premium, add_exp

# --- CONFIGURATION ---
AUTH_CHANNEL = "@Tomioka_Supportcore"  # Username of your group
SLOT_COOLDOWN = 5
user_cooldowns = {}

# 1. Helper Function to check subscription
async def is_subscribed(client, user_id):
    try:
        # This works in DM and Groups
        await client.get_chat_member(AUTH_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Sub check error: {e}")
        # If bot is not admin or group is not found, we allow the command
        return True

@Client.on_message(filters.command(["slot", "slots"]))
async def slot_handler(client, message):
    user_id = message.from_user.id
    
    # 2. Force Join Check
    if not await is_subscribed(client, user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Jᴏɪɴ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ", url=f"https://t.me/{AUTH_CHANNEL}")],
            [InlineKeyboardButton("🔄 Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{client.me.username}?start=check")]
        ])
        
        return await message.reply_text(
            f"❌ **Aᴄᴄᴇss Dᴇɴɪᴇᴅ!**\n\n"
            f"Yᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.\n"
            f"Jᴏɪɴ ᴀɴᴅ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs!",
            reply_markup=buttons
        )

    # 3. Logic starts here
    current_time = time.time()
    today = str(datetime.date.today())

    # Fetch User Data
    user_data = await users.find_one({"$or": [{"_id": user_id}, {"user_id": user_id}]}) or {}
    is_premium = await is_user_premium(user_id)
    
    # Daily Limit Logic
    last_slot_date = user_data.get("last_slot_date", "")
    spins_today = user_data.get("slots_count", 0) if last_slot_date == today else 0
    limit = 12 if is_premium else 10

    if last_slot_date == today and spins_today >= limit:
        return await message.reply_text(
            f"🚫 **Dᴀɪʟʏ Lɪᴍɪᴛ Rᴇᴀᴄʜᴇᴅ!**\n"
            f"Yᴏᴜ ʜᴀᴠᴇ ᴜsᴇᴅ ᴀʟʟ `{limit}` sᴘɪɴs ғᴏʀ ᴛᴏᴅᴀʏ.\n"
            f"⌛️ Cᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ!"
        )

    # Anti-Spam Cooldown
    if user_id in user_cooldowns and current_time - user_cooldowns[user_id] < SLOT_COOLDOWN:
        remaining = int(SLOT_COOLDOWN - (current_time - user_cooldowns[user_id]))
        return await message.reply_text(f"⏳ **Cᴏᴏʟᴅᴏᴡɴ!** Try again in `{remaining}s`.")

    # Spin the Slots
    slots = ["🍎", "🍋", "🍒", "🍇", "💎", "🎰"]
    res1, res2, res3 = random.choices(slots, k=3)
    jackpot = (res1 == res2 == res3)
    
    # Reward Logic
    if is_premium:
        dust_reward = random.randint(70, 150) if jackpot else random.randint(20, 80)
        exp_reward = random.randint(90, 130) if jackpot else random.randint(40, 70)
    else:
        dust_reward = random.randint(30, 70) if jackpot else random.randint(0, 20)
        exp_reward = random.randint(40, 60) if jackpot else random.randint(10, 30)

    # Database Update
    new_spins_count = spins_today + 1
    await users.update_one(
        {"$or": [{"user_id": user_id}, {"_id": user_id}]},
        {
            "$inc": {"stardust": float(dust_reward)},
            "$set": {"last_slot_date": today, "slots_count": new_spins_count}
        }
    )
    
    leveled_up, new_level = await add_exp(user_id, exp_reward)
    user_cooldowns[user_id] = current_time

    # Build Message
    premium_tag = "👑 [ᴘʀᴇᴍɪᴜᴍ]" if is_premium else ""
    remaining_spins = limit - new_spins_count
    
    msg = (
        f"🎰 **Sʟᴏᴛ Mᴀᴄʜɪɴᴇ** {premium_tag}\n"
        f"━━━━━━━━━━━━━━\n"
        f" | {res1} | {res2} | {res3} | \n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ **Wɪɴɴɪɴɢs:**\n"
        f"🌟 **Sᴛᴀʀᴅᴜsᴛ:** `+{dust_reward}`\n"
        f"✨ **EXP:** `+{exp_reward}`\n"
        f"🎫 **Sᴘɪɴs Lᴇғᴛ:** `{remaining_spins}/{limit}`"
    )

    if jackpot:
        msg += "\n🔥 **JACKPOT!** Your luck is insane!"
    
    if leveled_up:
        msg += f"\n\n🎊 **LEVEL UP!** You are now **Level {new_level}**!"
    
    await message.reply_text(msg)