import pandas as pd
import numpy as np
from datetime import datetime
from firebase.firebase import get_config, add_document, upload_file, read_collection, read_document, delete_document, read_document_with_filter, read_collection_with_composite_filter
from pytz import timezone
import os
from pytz import timezone
import sys
import yaml
import pyrebase
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from pytz import timezone
from typing import List, Dict
from google.cloud.firestore_v1.base_query import FieldFilter, Or, And
from google.cloud.firestore_v1.base_query import BaseCompositeFilter
import random
    
def download_information(agronom_tg_id: int):
    df = pd.DataFrame()
    info = read_collection_with_composite_filter(
        collection = "calendar_events",
        filters = [
            {
                "atribut": "agronomist_tg_id",
                "op": "==",
                "value": agronom_tg_id
            },
            {
                "atribut": "type",
                "op": "in",
                "value": ["Text only", "Visual only", "Text and Visual"]
            },
            {
                "atribut": "status",
                "op": "in",
                "value": ["notified_agronomist", "farmer_response"]
            }
        ],
        order = {
            "atribut": "timestamp_end",
            "desc": False
        }
    )
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
    return df
