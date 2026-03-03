from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from database import users, claims, characters
import html

@Client.on_message(filters.command("fav") & filters.group, group=-1)
async def set_favorite(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/fav [Character ID]`")

    # Clean and standardize the ID
    char_id = str(message.command[1].strip())

    # 1. Check ownership (Check both possible field names for safety)
    own_check = await claims.find_one({
        "user_id": user_id, 
        "$or": [{"char_id": char_id}, {"id": char_id}]
    })
    
    if not own_check:
        return await message.reply_text("❌ You don't own this character in your collection!")

    # 2. Get character details before updating
    char = await characters.find_one({"id": char_id})
    if not char:
        return await message.reply_text("❌ Character data not found in database!")

    # 3. Update User Profile
    await users.update_one(
        {"user_id": user_id},
        {"$set": {"favorite": char_id}},
        upsert=True
    )

    # 4. Media Handling (Video vs Photo)
    fav_name = html.escape(char['name'])
    media = char.get('file_id') or char.get('image')
    # Check if character is an AMV/Video
    is_video = "amv" in char.get('rarity', '').lower() or char.get("is_video", False)

    caption = f"⭐ <b>{fav_name}</b> has been set as your favorite!"

    if media:
        try:
            if is_video:
                await message.reply_video(video=media, caption=caption, parse_mode=ParseMode.HTML)
            else:
                await message.reply_photo(photo=media, caption=caption, parse_mode=ParseMode.HTML)
            return
        except Exception:
            pass # Fallback to text if media fails
    
    await message.reply_text(caption, parse_mode=ParseMode.HTML)