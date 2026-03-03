import random
from datetime import datetime, timedelta

AUCTIONS = []

async def spawn_daily_auction():
    waifu = random.choice([
        {"name": "Special Auction Waifu", "rarity": 4, "anime": "Anime X"},
        {"name": "Limited Auction Waifu", "rarity": 5, "anime": "Anime Y"},
        {"name": "Celestial Auction Waifu", "rarity": 6, "anime": "Anime Z"}
    ])
    auction = {
        "name": waifu["name"],
        "series": waifu["anime"],
        "id": random.randint(1000,9999),
        "rarity": waifu["rarity"],
        "current_bid": 0,
        "remaining": timedelta(hours=24),
        "starting_bid": 100,
        "total_bidders": 0,
        "current_bidder": None
    }
    AUCTIONS.append(auction)
    return auction
