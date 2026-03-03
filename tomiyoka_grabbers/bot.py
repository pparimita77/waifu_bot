from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

class TomiokaBot(Client):
    def __init__(self):
        super().__init__(
            "TomiokaGiyu",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="handlers")
        )

if __name__ == "__main__":
    print("🌊 Tomioka Giyu Bot is Starting...")
    TomiokaBot().run()