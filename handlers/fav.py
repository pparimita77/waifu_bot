from pyrogram import Client, filters
from database import users, claims, characters

@Client.on_message(filters.command("fav"))
async def set_favorite(client, message):
    if len(message.command) < 2:
        return await message.reply_text("📝 **Usage:** `/fav <character_id>`\nExample: `/fav 10`")

    user_id = message.from_user.id
    char_id = message.command[1].strip()

    # 1. Verify ownership in claims
    is_owned = await claims.find_one({"user_id": user_id, "char_id": char_id})
    
    if not is_owned:
        return await message.reply_text("❌ You don't own this character!")

    # 2. Update user's favorite ID
    await users.update_one(
        {"_id": user_id},
        {"$set": {"fav_id": char_id}},
        upsert=True
    )

    await message.reply_text(f"✅ **{is_owned['name']}** has been set as your favorite character!")