from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import users, claims

async def get_personal_rank(user_id, category):
    """Calculates the rank of a specific user in a category."""
    if category == "collection":
        # Rank by number of waifus owned
        pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        all_counts = await claims.aggregate(pipeline).to_list(None)
        for i, entry in enumerate(all_counts, 1):
            if entry["_id"] == user_id:
                return i, entry["count"]
    else:
        # Rank by Gems or Stardust
        user_data = await users.find_one({"_id": user_id})
        if not user_data:
            return "N/A", 0
        
        value = user_data.get(category, 0)
        # Count how many users have a higher value than this user
        rank = await users.count_documents({category: {"$gt": value}})
        return rank + 1, value
    
    return "N/A", 0

async def get_leaderboard_text(user_id, category="gems"):
    titles = {
        "gems": "💎 Gᴇᴍs Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ",
        "stardust": "🌟 Sᴛᴀʀᴅᴜsᴛ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ",
        "collection": "🌸 Hᴀʀᴇᴍ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ"
    }
    
    text = f"🏆 **{titles[category]}** 🏆\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 1. Fetch Top 10
    if category == "collection":
        pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_users = await claims.aggregate(pipeline).to_list(10)
    else:
        top_users = await users.find({}, {category: 1, "first_name": 1}).sort(category, -1).limit(10).to_list(10)

    # 2. Build the list text
    for i, user in enumerate(top_users, 1):
        name = user.get("first_name", "Unknown")
        if category == "collection":
            # For Collection, we use the ID as a placeholder
            val = user.get("count", 0)
            text += f"{i}. ID: `{user['_id']}` — **{val}** 🌸\n"
        else:
            val = user.get(category, 0)
            text += f"{i}. **{name}** — `{val}`\n"

    # 3. Add Personal Rank Section
    rank, user_val = await get_personal_rank(user_id, category)
    text += "\n━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👤 **Yᴏᴜʀ Pᴏsɪᴛɪᴏɴ:** `#{rank}` — `{user_val}`"
    
    return text

@Client.on_message(filters.command(["leaderboard", "top"]))
async def leaderboard_cmd(client, message):
    user_id = message.from_user.id
    text = await get_leaderboard_text(user_id, "gems")
    
    buttons = [
        [
            InlineKeyboardButton("💎 Gems", callback_data="lb_gems"),
            InlineKeyboardButton("🌟 Stardust", callback_data="lb_stardust")
        ],
        [
            InlineKeyboardButton("🌸 Collection", callback_data="lb_collection")
        ]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^lb_"))
async def lb_callback(client, query: CallbackQuery):
    category = query.data.split("_")[1]
    user_id = query.from_user.id
    text = await get_leaderboard_text(user_id, category)
    
    buttons = [
        [
            InlineKeyboardButton("💎 Gems", callback_data="lb_gems"),
            InlineKeyboardButton("🌟 Stardust", callback_data="lb_stardust")
        ],
        [
            InlineKeyboardButton("🌸 Collection", callback_data="lb_collection")
        ]
    ]
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))