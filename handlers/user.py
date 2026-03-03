from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from utils import check_join, get_random_char, is_premium, RARITY_DICT
from database import users

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update):
        await update.message.reply_text("Please join the required channels to use the bot.")
        return
    await update.message.reply_text(
        "🌊 Welcome to Tomioka Giyuu Grabbers Bot\n\n"
        "Like still water hiding unmatched strength...\n"
        "Summon waifus, claim your favorites, and build a collection worthy of a true slayer! 💖"
    )

start_handler = CommandHandler("start", start)

# CLAIM
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_join(update):
        await update.message.reply_text("Please join the required channels first!")
        return
    
    user_data = users.find_one({"user_id": user_id}) or {"daily_claims": 0}
    if user_data.get("daily_claims", 0) >= 1 and not is_premium(user_id):
        await update.message.reply_text("You reached your daily limit! Activate subscription for more.")
        return
    
    char = get_random_char(user_id)
    if char:
        await update.message.reply_text(
            f"🌊 This waifu now belongs to you {update.effective_user.full_name} 💙\n"
            f"🌸 ID: {char['_id']}\n"
            f"💫 Name: {char['name']}\n"
            f"🌈 Rarity: {RARITY_DICT.get(char['rarity'])}\n"
            f"🍜 Source: {char['source']}"
        )
    else:
        await update.message.reply_text("No waifus available now. Try again later!")

claim_handler = CommandHandler("claim", claim)

# BALANCE
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = users.find_one({"user_id": user_id}) or {"gems": 0, "stardust": 0, "emerald": 0}
    await update.message.reply_text(
        f"⛩️ {update.effective_user.full_name}!\n"
        f"💎 Gems: {data.get('gems',0)}\n"
        f"🌟 Stardust: {data.get('stardust',0)}\n"
        f"💠 Emerald: {data.get('emerald',0)}"
    )

balance_handler = CommandHandler("balance", balance)

# MODE
async def mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚪ Common", callback_data="mode_1"),
         InlineKeyboardButton("💮 Legendary", callback_data="mode_2"),
         InlineKeyboardButton("🏵️ Rare", callback_data="mode_3")],
        [InlineKeyboardButton("🫧 Special", callback_data="mode_4"),
         InlineKeyboardButton("🔮 Limited", callback_data="mode_5"),
         InlineKeyboardButton("🎐 Celestial", callback_data="mode_6")],
        [InlineKeyboardButton("💸 Expensive", callback_data="mode_7"),
         InlineKeyboardButton("🧧 Giveaway", callback_data="mode_8"),
         InlineKeyboardButton("🍂 Seasonal", callback_data="mode_9")],
        [InlineKeyboardButton("💝 Valentine", callback_data="mode_10"),
         InlineKeyboardButton("🎥 AMV", callback_data="mode_11"),
         InlineKeyboardButton("🔖 Manga", callback_data="mode_12")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌟 Select a rarity mode!", reply_markup=reply_markup)

mode_handler = CommandHandler("mode", mode)

# REDEEM
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Redeem your code feature coming soon!")
redeem_handler = CommandHandler("redeem", redeem)

# WREDEEM
async def wredeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Exclusive waifu redeem coming soon!")
wredeem_handler = CommandHandler("wredeem", wredeem)

# SHOP
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Shop is under construction!")
shop_handler = CommandHandler("shop", shop)

# BONUS
async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Daily and weekly bonus claimed!")
bonus_handler = CommandHandler("bonus", bonus)

# GRAB
async def grab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Grab a waifu using /grab command!")
grab_handler = CommandHandler("grab", grab)

# FAV
async def fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Make a waifu favourite using /fav <id>")
fav_handler = CommandHandler("fav", fav)

# PROFILE
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("View profile info using /profile")
profile_handler = CommandHandler("profile", profile)

# SLOTS
async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Play slots using /slots")
slots_handler = CommandHandler("slots", slots)

# MARRY
async def marry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Marry a waifu using /marry <id>")
marry_handler = CommandHandler("marry", marry)

# PROPOSE
async def propose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Propose a waifu using /propose <id>")
propose_handler = CommandHandler("propose", propose)

# REFER
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Refer friends using /refer <id>")
refer_handler = CommandHandler("refer", refer)

# PAY
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pay coins using /pay <amount>")
pay_handler = CommandHandler("pay", pay)

# SEARCH
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Search waifu by name using /search <name>")
search_handler = CommandHandler("search", search)

# FIND
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Search waifu by id using /find <id>")
find_handler = CommandHandler("find", find)

# W-FIND
async def wfind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("See character details by /wfind <id>")
wfind_handler = CommandHandler("wfind", wfind)
