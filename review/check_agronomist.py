from firebase.firebase import  read_collection

def check_agronomist(tg_id: int) -> bool:
    '''
    Check farmer with tg_id from telegram message to exist in collection "farmers"
    
    Args:
        tg_id: int
            tg_id from telegram message
    '''
    agronomists = read_collection("agronomists")
    tg_id_agronomists = [agronom["data"]["tg_id"] for agronom in agronomists]
    return tg_id in tg_id_agronomists
