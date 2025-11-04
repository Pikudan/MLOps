import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from firebase.firebase import (add_document, read_collection, 
                      read_document, delete_document, read_document_with_filter, update_document,
                      read_collection_with_composite_filter, read_collection_with_composite_filter)


def download_problems_for_support(collection, problem, id, person, start_time):
    df = pd.DataFrame()
    info = read_collection_with_composite_filter(
        collection,
        [{'atribut': 'problem', 'op': '==', 'value': problem},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': id},
        {'atribut': 'time', 'op': '>=', 'value': start_time}]
    )
    if not info:
        return df
    
    doc = []
    for i in info:
        data = i["data"]
        data["person"] = person
        data["document_id"] = i["document_id"]
        doc.append(data)
    df = pd.DataFrame.from_dict(doc)

    return df

'''
def download_information(collection: str, op=None, status=False):
    df = pd.DataFrame()
    if op is None and status is False:
        info = read_collection(collection)
    elif op is not None:
        if status is False:
            info = read_document_with_filter('user_telegram_id', '==', op, collection)
        else:
            info = read_collection_with_composite_filter(collection,[{'atribut': 'status', 'op': '==', 'value': 'open'},
                                                {'atribut': 'user_telegram_id', 'op': '==', 'value': op}])
    doc = {'document_id': []}
    for i in info:
        doc['document_id'].append(i['document_id'])
        for j in i['data'].keys():
            if j in doc.keys():
                doc[j].append(i['data'][j])
            else:
                doc[j] = [i['data'][j]]
    for key in doc.keys():
        df[key] = doc[key]
    return df
'''
def to_DataFrame_information(info):
    df = pd.DataFrame()
    doc = {'document_id': []}
    for i in info:
        doc['document_id'].append(i['document_id'])
        for j in i['data'].keys():
            if j in doc.keys():
                doc[j].append(i['data'][j])
            else:
                doc[j] = [i['data'][j]]
    for key in doc.keys():
        df[key] = doc[key]
    if 'timestamp_end' in doc.keys():
        df = df.sort_values(by='timestamp_end', ascending=False)
    if 'time' in doc.keys():
        df = df.sort_values(by=['time', 'message_id_chat'])
    return df

def add_information(collection, document, df):
    document['document_id'] = add_document(document, collection)
    document = pd.DataFrame(document, index=[0])
    df = pd.concat([df, document], ignore_index=True)
    return df

def merge_and_sortes_message_about_problems(problem, id, start_time):
    
    df1 = download_problems_for_support('telegram_message_from_support_for_farmer', problem, id, 'agronomist', start_time)
    df2 = download_problems_for_support('telegram_message_from_farmer_for_support', problem, id, 'You', start_time)
    if df1.empty and not df2.empty:
         merged_df = df2
    elif df2.empty and not df1.empty:
        merged_df = df1
    if df1.empty and df2.empty:
        return pd.DataFrame()
    else:
        merged_df = pd.concat([df1, df2])
    merged_df = merged_df.reset_index(drop=True)
    sorted_df = merged_df.sort_values(by=['time', 'message_id_chat'])
    return sorted_df

# def change_count_of_new_message()

'''
def download_unread_message_for_support(id):
    df = to_DataFrame_information(read_collection_with_composite_filter(
        'telegram_message_from_farmer_for_support',
        [{'atribut': 'status', 'op': '==', 'value': 'unread'},
         {'atribut': 'user_telegram_id', 'op': '==', 'value': id}]))
    return df
'''
