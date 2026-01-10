from pyrogram import Client, filters
from database import users

@Client.on_message(filters.command(["balance", "bal"]))
async def balance(client, message):
    try:
        user_id = message.from_user.id
        
        # 1. Fetch user data
        user_data = await users.find_one({"_id": user_id})
        
        # 2. If user doesn't exist, we assume 0
        if not user_data:
            gems = 0
            stardust = 0
            emerald = 0
        else:
            gems = user_data.get('gems', 0)
            stardust = user_data.get('stardust', 0)
            emerald = user_data.get('emerald', 0)
        
        # 3. Format the text
        text = (
            f"⛩️ Kᴏɴɴɪᴄʜɪᴡᴀ {message.from_user.first_name}-Sᴀɴ! 💫\n\n"
            f"🏦 **Hᴇʀᴇ's Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ** 🏦\n\n"
            f"💎 **Gᴇᴍs:** `{gems}`\n"
            f"🌟 **Sᴛᴀʀᴅᴜsᴛ:** `{stardust}`\n"
            f"💠 **Eᴍᴇʀᴀʟᴅ:** `{emerald}`"
        )
        
        await message.reply_text(text)
        
    except Exception as e:
        # This will tell you EXACTLY why it's failing in your terminal
        print(f"Error in balance command: {e}")