import random
import time
from pyrogram import Client, filters
from database import users

# Cooldown (30 seconds)
SLOT_COOLDOWN = 30 
user_cooldowns = {}

@Client.on_message(filters.command("slot"))
async def slot_exp(client, message):
    user_id = message.from_user.id
    current_time = time.time()

    # 1. Cooldown Check
    if user_id in user_cooldowns and current_time - user_cooldowns[user_id] < SLOT_COOLDOWN:
        remaining = int(SLOT_COOLDOWN - (current_time - user_cooldowns[user_id]))
        return await message.reply_text(f"⏳ **Cooldown!** Try again in `{remaining}s`.")

    # 2. Spin the Slots
    slots = ["🍎", "🍋", "🍒", "🍇", "💎", "🎰"]
    res1, res2, res3 = random.choices(slots, k=3)
    
    # 3. Logic: Standard EXP vs Jackpot
    if res1 == res2 == res3:
        earned_exp = 100
        jackpot = True
    else:
        earned_exp = random.randint(5, 11)
        jackpot = False
    
    # 4. Update Database
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"total_exp": earned_exp}},
        upsert=True
    )
    user_cooldowns[user_id] = current_time

    # 5. Build Result Message
    msg = (
        f"🎰 **Sʟᴏᴛ Mᴀᴄʜɪɴᴇ** 🎰\n"
        f"━━━━━━━━━━━━━━\n"
        f"| {res1} | {res2} | {res3} |\n"
        f"━━━━━━━━━━━━━━\n"
    )
    if jackpot:
        msg += f"🔥 **JACKPOT!** You earned **+{earned_exp} EXP**!"
    else:
        msg += f"✨ You earned **+{earned_exp} EXP**!"
    
    await message.reply_text(msg)