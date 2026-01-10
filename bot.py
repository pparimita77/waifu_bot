from pyrogram import Client
import config

class TomiokaBot(Client):
    def __init__(self):
        super().__init__(
            "TomiokaV2", 
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="handlers"),
            ipv6=False  # <--- ADD THIS LINE HERE
        )

if __name__ == "__main__":
    print("🌊 Tomioka Giyu Grabber Bot is Starting...")
    TomiokaBot().run()