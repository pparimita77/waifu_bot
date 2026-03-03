import random

async def slots(user_id, db):
    # Simple slot system
    gems_won = random.randint(20, 50)
    db[str(user_id)]["gems"] += gems_won
    return gems_won

async def dice(user_id, db):
    result = random.randint(1, 6)
    return result
