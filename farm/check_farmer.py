from firebase.firebase import  read_collection

def check_farmer(tg_id: int) -> bool:
    '''
    Check farmer with tg_id from telegram message to exist in collection "farmers"
    
    Args:
        tg_id: int
            tg_id from telegram message
    '''
    farmers = read_collection("farmers")
    tg_id_farmers = [farmer["data"]["tg_id"] for farmer in farmers]
    return tg_id in tg_id_farmers
