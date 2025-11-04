import pandas as pd


def event_brief_information(pagination_df):
    start = pagination_df.get_page_number()
    finish = (pagination_df.get_page_number() + 1)
    msg = ''
    for i in range(start, finish):
        title = str(pagination_df.get_DataFrame().loc[i:i, 'title'].values[0]).upper()
        date_end = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_end'].values[0])
        month_name = date_end.strftime("%B")
        day = date_end.day
        year = date_end.year
        msg += f"*{title}*\n*Expiration date:* {day} {month_name} {year}\n"
    return msg

def event_full_information(pagination_df):
    start = pagination_df.get_page_number()
    finish = (pagination_df.get_page_number() + 1)
    msg = event_brief_information(pagination_df)
    for i in range(start, finish):
        date_begin = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_begin'].values[0])
        date_create = pd.to_datetime(pagination_df.get_DataFrame().loc[i:i, 'timestamp_creates'].values[0])
        month_name_begin = date_begin.strftime("%B")
        day_begin = date_begin.day
        year_begin = date_begin.year
        month_name_create = date_create.strftime("%B")
        day_create = date_create.day
        year_create = date_create.year
        info = str(pagination_df.get_DataFrame().loc[i:i, 'info'].values[0])
        status = str(pagination_df.get_DataFrame().loc[i:i, 'status'].values[0]).replace('_', ' ')
        msg += f"*Start date:* {day_begin} {month_name_begin} {year_begin}\n*Create date:* {day_create} {month_name_create} {year_create}\n*Info:* {info}\n*Status:* {status}\n"
    return msg

def msg_from_chating(doc):
    doc = doc.to_dict()
    msg = f"_{doc['person']}_\n_{doc['time'].strftime('%Y-%m-%d %H:%M:%S')}_\n\n{doc['text']}"
    return msg

def support_history_msg(doc):
    doc = doc.to_dict()
    msg = f"*TIME FROM FARMER:* {doc['time_from_farmer'].strftime('%Y-%m-%d %H-%M-%S')}\n*TIME FROM AGRONOMIST:* {doc['time_from_agronomist'].strftime('%Y-%m-%d %H-%M-%S')}\n*MESSAGE ID:* {doc['message_id']}\n*FROM FARMER:* {doc['farmer_tg_id']}\n\n*Farmer*:\n{doc['text_from_farmer']}\n\n*Agronomist:*\n{doc['text_from_agronomist']}"
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
                    msg.append(f"_{doc['person']}_")
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
