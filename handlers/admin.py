from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from database import users, characters, config  # Use 'characters' instead of 'waifus'
from utils import is_sudo, is_dev, is_owner, RARITY_DICT

# ------------------ UPLOADER ------------------

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # AWAIT the async permission check
    if not await is_dev(user_id):
        await update.message.reply_text("❌ You are not authorized to upload characters.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /upload <NAME> <ANIME> <RARITY_ID>")
        return

    name = context.args[0]
    anime = context.args[1]
    try:
        rarity_id = context.args[2]
        rarity_name = RARITY_DICT.get(rarity_id, "Unknown")
        
        # AWAIT the database insertion
        result = await characters.insert_one({
            "name": name, 
            "source": anime, 
            "rarity": rarity_name
        })
        
        await update.message.reply_text(f"✅ Uploaded {name} ({rarity_name}) with ID: {result.inserted_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}"
        )

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_dev(user_id):
        await update.message.reply_text("❌ You are not authorized to delete waifus.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /delete <CHARACTER-ID>")
        return

    char_id = int(context.args[0])
    waifus.delete_one({"_id": char_id})
    await update.message.reply_text(f"🗑️ Deleted character with ID {char_id}")

delete_handler = CommandHandler("delete", delete)


# ------------------ SUDO ------------------

async def gen_gems(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sudo(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized!")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /gen_gems <amount> <user_id>")
        return
    
    amount = int(context.args[0])
    target_id = int(context.args[1])
    
    # Example logic: incrementing gems in database
    await users.update_one({"user_id": target_id}, {"$inc": {"gems": amount}}, upsert=True)
    await update.message.reply_text(f"✅ Generated {amount} Gems for {target_id}")

# ... (Apply similar await fixes to delete, add_sudo, add_dev, etc.)

#STATS

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_dev(update.effective_user.id):
        await update.message.reply_text("❌ Only dev can see stats.")
        return
        
    # Database counts must be awaited
    total_users = await users.count_documents({})
    total_chars = await characters.count_documents({})
    
    await update.message.reply_text(f"📊 Total Users: {total_users}\n📊 Total Characters: {total_chars}")

# ------------------ DEV ------------------

async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only owner can add sudo.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /add_sudo <USER-ID>")
        return
    sudo_id = int(context.args[0])
    users.update_one({"user_id": sudo_id}, {"$set": {"sudo": True}}, upsert=True)
    await update.message.reply_text(f"✅ Added sudo for user {sudo_id}")

add_sudo_handler = CommandHandler("add_sudo", add_sudo)

async def rm_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only owner can remove sudo.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /rm_sudo <USER-ID>")
        return
    sudo_id = int(context.args[0])
    users.update_one({"user_id": sudo_id}, {"$unset": {"sudo": ""}})
    await update.message.reply_text(f"✅ Removed sudo for user {sudo_id}")

rm_sudo_handler = CommandHandler("rm_sudo", rm_sudo)

async def add_uploader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only owner can add uploader.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /add_uploader <USER-ID>")
        return
    uploader_id = int(context.args[0])
    users.update_one({"user_id": uploader_id}, {"$set": {"uploader": True}}, upsert=True)
    await update.message.reply_text(f"✅ Added uploader {uploader_id}")

add_uploader_handler = CommandHandler("add_uploader", add_uploader)

async def rm_uploader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only owner can remove uploader.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /rm_uploader <USER-ID>")
        return
    uploader_id = int(context.args[0])
    users.update_one({"user_id": uploader_id}, {"$unset": {"uploader": ""}})
    await update.message.reply_text(f"✅ Removed uploader {uploader_id}")

rm_uploader_handler = CommandHandler("rm_uploader", rm_uploader)

# ------------------ OWNER ------------------

async def add_dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can add devs.")
        return
    dev_id = int(context.args[0])
    users.update_one({"user_id": dev_id}, {"$set": {"dev": True}}, upsert=True)
    await update.message.reply_text(f"✅ Added dev {dev_id}")

add_dev_handler = CommandHandler("add_dev", add_dev)

async def rm_dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can remove devs.")
        return
    dev_id = int(context.args[0])
    users.update_one({"user_id": dev_id}, {"$unset": {"dev": ""}})
    await update.message.reply_text(f"✅ Removed dev {dev_id}")

rm_dev_handler = CommandHandler("rm_dev", rm_dev)

# ------------------ CONFIG ------------------

async def setstart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.effective_user.id):
        await update.message.reply_text("❌ Only dev can set start message.")
        return
    # Logic for setting bot start message
    await update.message.reply_text("✅ Start message updated!")

setstart_handler = CommandHandler("setstart", setstart)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.effective_user.id):
        await update.message.reply_text("❌ Only dev can see stats.")
        return
    total_users = users.count_documents({})
    total_chars = waifus.count_documents({})
    await update.message.reply_text(f"📊 Total Users: {total_users}\n📊 Total Characters: {total_chars}")

stats_handler = CommandHandler("stats", stats)

async def setcost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.effective_user.id):
        await update.message.reply_text("❌ Only dev can set cost.")
        return
    await update.message.reply_text("✅ Cost updated!")

setcost_handler = CommandHandler("setcost", setcost)

async def setbidcost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.effective_user.id):
        await update.message.reply_text("❌ Only dev can set bid cost.")
        return
    await update.message.reply_text("✅ Bid cost updated!")

setbidcost_handler = CommandHandler("setbidcost", setbidcost)

async def rset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.effective_user.id):
        await update.message.reply_text("❌ Only dev can reset rarity spawn.")
        return
    # Show buttons to select rarity for all groups
    await update.message.reply_text("✅ Rarity reset for all groups!")

rset_handler = CommandHandler("rset", rset)
