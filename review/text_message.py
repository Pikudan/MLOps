import pandas as pd
from pagination_info import DataFramePaginator
from collection_editer import download_information

def event_brief_information(pagination_df):
    i = pagination_df.get_page_number()
    title = str(pagination_df.get_DataFrame().loc[i:i, 'title'].values[0])
    info = str(pagination_df.get_DataFrame().loc[i:i, 'info'].values[0])
    type = str(pagination_df.get_DataFrame().loc[i:i, 'type'].values[0])
    msg = f"*Title:* {title}\n*Type:* {type}\n*Info:* {info}"
    return msg
