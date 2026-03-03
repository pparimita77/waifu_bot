from config import OWNER_ID, DEVS

def get_auth_users():
    auth = []
    # Add Owner(s)
    if isinstance(OWNER_ID, list):
        auth.extend(OWNER_ID)
    else:
        auth.append(OWNER_ID)
    
    # Add Dev(s)
    if DEVS:
        if isinstance(DEVS, list):
            auth.extend(DEVS)
        else:
            auth.append(DEVS)
            
    # Return unique integers only
    return list(set(int(x) for x in auth if x))

# Pre-calculate it once
AUTHORIZED = get_auth_users()