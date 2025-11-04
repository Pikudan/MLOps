import pandas as pd
from pagination_info import DataFramePaginator
from collection_editer import download_information
from bd_and_DataFrame import merge_and_sortes_message_about_problems


def event_brief_information(pagination_df):
    i = pagination_df.get_page_number()
    title = str(pagination_df.get_DataFrame().loc[i:i, 'title'].values[0])
    date_begin = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_begin'].values[0]).strftime("%d %B %Y")
    date_end = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_end'].values[0]).strftime("%d %B %Y")
    msg = f"<p><b>Title:</b> {title}<br/><b>Available From:</b> {date_begin}<br/><b>Complete By:</b> {date_end}</p>"
    status = str(pagination_df.get_DataFrame().loc[i:i, 'status'].values[0])
    if status == "refused":
        msg += f'        <hr/><p>Thank you for confirming the completion of this task!<br/><br/>Unfortunately, upon careful review, we have to ask you to resubmit your evidence. Press “More Information” for guidance.</p>'
    return msg

def event_full_information(pagination_df):
    i = pagination_df.get_page_number()
    title = str(pagination_df.get_DataFrame().loc[i:i, 'title'].values[0])
    date_begin = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_begin'].values[0]).strftime("%d %B %Y")
    date_end = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_end'].values[0]).strftime("%d %B %Y")
    info = str(pagination_df.get_DataFrame().loc[i:i, 'info'].values[0])
    type = str(pagination_df.get_DataFrame().loc[i:i, 'type'].values[0])
    msg = f"*Title:* {title}\n*Task Description:* {info}\n*Reporting style:* {type}\n*Available From:* {date_begin}\n*Complete By:* {date_end}"
    return msg

def event_without_confirm(pagination_df):
    i = pagination_df.get_page_number()
    title = str(pagination_df.get_DataFrame().loc[i:i, 'title'].values[0])
    info = str(pagination_df.get_DataFrame().loc[i:i, 'info'].values[0])
    type = str(pagination_df.get_DataFrame().loc[i:i, 'type'].values[0])
    date_begin = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_begin'].values[0]).strftime("%d %B %Y")
    date_end = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_end'].values[0]).strftime("%d %B %Y")
    msg = f"*Title:* {title}\n*Task Description:* {info}\n*Reporting style:* {type}\n*Available From:* {date_begin}\n*Complete By:* {date_end}\n\n*Have you completed?*"
    return msg
    
def msg_for_support(df):
    msg = []
    days = {}
    flag = True
    month_name_pred, day_pred = None, None
    for index, row in df.iterrows():
        if row["type"] == "text":
            month_name = row['time'].strftime("%B")
            day = row['time'].day
            doc = row.to_dict()
            if flag:
                flag = False
                days[index] = f"*{day} {month_name}*"
                if doc['person'] == 'agronomist' and doc['status'] == 'new':
                    msg.append(f"*{doc['person']}*\n*{doc['text']}*")
                else:
                    msg.append(f"_{doc['person']}_\n{doc['text']}")
            else:
                if month_name_pred ==  month_name and day_pred == day:
                    if doc['person'] == 'agronomist' and doc['status'] == 'new':
                        msg.append(f"*{doc['person']}*\n*{doc['text']}*")
                    else:
                        msg.append(f"_{doc['person']}_\n{doc['text']}")
                else:
                    days["index"] = f"*{day} {month_name}*"
                    if doc['person'] == 'agronomist' and doc['status'] == 'new':
                        msg.append(f"*{doc['person']}*\n*{doc['text']}*")
                    else:

                        msg.append(f"{doc['person']}_\n{doc['text']}")
        else:
            month_name = row['time'].strftime("%B")
            day = row['time'].day
            doc = row.to_dict()
            if flag:
                flag = False
                days[index] = f"*{day} {month_name}*"
                if doc['person'] == 'agronomist' and doc['status'] == 'new':
                    msg.append(f"*{doc['person']}*")
                else:
                    msg.append(f"_{day} {month_name}_\n\n_{doc['person']}_")
            else:
                if month_name_pred ==  month_name and day_pred == day:
                    if doc['person'] == 'agronomist' and doc['status'] == 'new':
                        msg.append(f"*{doc['person']}*")
                    else:
                        msg.append(f"_{doc['person']}_")
                else:
                    days[index] = f"*{day} {month_name}*"
                    if doc['person'] == 'agronomist' and doc['status'] == 'new':
                        msg.append(f"*{doc['person']}*")
                    else:
                        msg.append(f"_{doc['person']}_")
        month_name_pred, day_pred = month_name, day
    return msg, days
