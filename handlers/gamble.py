import random
from pyrogram import Client, filters
from database import users

@Client.on_message(filters.command("gamble"))
async def gamble_gems(client, message):
    user_id = message.from_user.id
    
    # 1. Parse the bet amount
    if len(message.command) < 2:
        return await message.reply_text("💎 **Usage:** `/gamble <amount>`\nExample: `/gamble 10` or `/gamble all`")

    user_data = await users.find_one({"_id": user_id}) or {}
    # Switching from 'balance' to 'gems'
    gems_balance = user_data.get("gems", 0)

    if gems_balance <= 0:
        return await message.reply_text("❌ You don't have any **Gems** to gamble! Use `/daily` or `/slot` to earn some.")

    bet_input = message.command[1].lower()
    
    if bet_input == "all":
        bet = gems_balance
    elif bet_input.isdigit():
        bet = int(bet_input)
    else:
        return await message.reply_text("❌ Please enter a valid number or 'all'.")

    # 2. Validation
    if bet < 1:
        return await message.reply_text("⚠️ Minimum bet is **1 Gem**.")
    if bet > gems_balance:
        return await message.reply_text(f"❌ You don't have enough Gems! Your balance: `💎 {gems_balance:,}`")

    # 3. The Gamble Logic
    # 45% Win, 45% Lose, 10% Jackpot (3x)
    chance = random.randint(1, 100)
    
    if chance <= 10:
        # JACKPOT WIN (3x)
        winnings = bet * 2 # You keep your bet + gain 2x more
        await users.update_one({"_id": user_id}, {"$inc": {"gems": winnings}})
        new_balance = gems_balance + winnings
        result = f"🔥 **JACKPOT!** You tripled your bet!\n💰 **Winnings:** `💎 {winnings + bet:,}`"
    
    elif chance <= 50:
        # NORMAL WIN (Double)
        await users.update_one({"_id": user_id}, {"$inc": {"gems": bet}})
        new_balance = gems_balance + bet
        result = f"🎉 **YOU WON!** Your gems doubled.\n💰 **Winnings:** `💎 {bet * 2:,}`"
    
    else:
        # LOSS
        await users.update_one({"_id": user_id}, {"$inc": {"gems": -bet}})
        new_balance = gems_balance - bet
        result = f"💀 **YOU LOST!** Better luck next time.\n📉 **Remaining:** `💎 {new_balance:,}`"

    # 4. Final Message
    await message.reply_text(
        f"🎲 **Gᴇᴍ Gᴀᴍʙʟᴇ** 🎲\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 **User:** {message.from_user.mention}\n"
        f"💵 **Bet Amount:** `💎 {bet:,}`\n\n"
        f"{result}\n"
        f"━━━━━━━━━━━━━━"
    )