from pyrogram.errors import UserNotParticipant

AUTH_CHANNEL = "@Tomioka_Supportcore" # Your Group Username

async def is_subscribed(client, user_id):
    try:
        member = await client.get_chat_member(AUTH_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        # If the bot isn't an admin in the group, it can't check
        return True