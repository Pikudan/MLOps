from collection_editer import download_information
def count_message(farmer_id: int):
    df = download_information(int(farmer_id), 'problems_for_support')
    buttons = []
    count = 0
    if df.empty:
        return count
    else:
        for index, row in df.iterrows():
            button = row.to_dict()
            count += button['number_of_messages_from_agro']
    return count

