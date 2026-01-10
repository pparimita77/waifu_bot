
RARITY_MAP = {
    "1": {"name": "Common", "emoji": "?", "value": 500},
    "2": {"name": "Legendary", "emoji": "??", "value": 5000},
    "3": {"name": "Rare", "emoji": "???", "value": 1500},
    "4": {"name": "Special", "emoji": "??", "value": 3000},
    "5": {"name": "Limited", "emoji": "??", "value": 10000},
    "6": {"name": "Celestial", "emoji": "??", "value": 15000},
    "7": {"name": "Manga", "emoji": "??", "value": 2500},
    "8": {"name": "Expensive", "emoji": "??", "value": 20000},
    "9": {"name": "Giveaway", "emoji": "??", "value": 0},
    "10": {"name": "Seasonal", "emoji": "??", "value": 4000},
    "11": {"name": "Valentine", "emoji": "??", "value": 4500},
    "12": {"name": "AMV", "emoji": "??", "value": 6000}
}

def get_rarity_emoji(rarity_id):
    rarity = RARITY_MAP.get(str(rarity_id))
    return rarity["emoji"] if rarity else "?"

def get_rarity_info(rarity_id):
    return RARITY_MAP.get(str(rarity_id))

def get_rarity_name(rarity_id):
    rarity = RARITY_MAP.get(str(rarity_id))
    return rarity["name"] if rarity else "Unknown"

