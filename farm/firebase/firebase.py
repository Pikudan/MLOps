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
from google.cloud.firestore_v1.base_query import FieldFilter
import random

def get_config() -> Dict:
    """Read firebase_config.yaml in this directory.

    Returns:
      dictionary

    Raises:
      OSError: Could not open/read file.
    """
    config_path = Path(__file__).parent.parent / "firebase/firebase_config.yaml"
    try:
        file = open(config_path, 'rb')
        with file:
            firebase_config = yaml.safe_load(file)
        file.close()
        return firebase_config
    except OSError:
        print("Could not open/read file: {}".format(config_path))
        return None


def create_config(data: Dict):
    """Create firebase_config.yaml in this directory.

    Args:
      data: dict
          data to write in config_path

    Raises:
      OSError: Could not open/read file.
    """
    config_path = Path(__file__).parent.parent / "firebase/firebase_config.yaml"
    try:
        file = open(config_path, "w")
        with file:
            yaml.dump(data, file, default_flow_style=False)
        file.close()
    except OSError:
        print("Could not open/read file: {}".format(config_path))
    
 
 
 
def save_changing(name_function: str, time_of_changing: str, params: Dict):
    """Save changing of collection from Firebase in format
    {
        "name_function":
        "time_of_changing":
        "params":
    }

    Args:
       name_function: str
           name function was using
       time_of_changing: str
           time of changing
       params: Dict
           parameters for function with name function

    """
    firebase_config = get_config()
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection_name = "history changed storage"
    db.collection(collection_name).add(
        {
            "name_function": name_function,
            "time_of_changing": time_of_changing,
            "params": params
        }
    )
       
def create_collection(collection: str, data: List[Dict]):
    """Create collection from Firebase.

    Args:
      collection: str
          name colleection on cloud
      data: List[Dict]
          data for write in collection

    Raises:
      NameError: The collection name exists in config file. Or Document(s) already exist in the collection.
    """
    
    firebase_config = get_config()
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    if len(db.collection(collection).get()) != 0:
        print("Document(s) already exist in the collection: {}".format(db.collection(collection).get()))
    else:
        document_ids = []
        for document in data:
            gl = db.collection(collection).add(document)
            
        tz=timezone(firebase_config['timezone'])
        time_of_changing = datetime.now(tz=tz)
        save_changing(
            name_function = "create_collection",
            time_of_changing = time_of_changing,
            params = {
                "collection": collection,
                "data": data
            }
        )
            
def read_collection(collection: str) -> List[Dict]:
    """Read collection from Firebase
       
    Args:
        collection: str
            name collection on cloud.

    Returns:
        List[Dict] - list of dictinary:
            {
                "document_id": document id from collection
                "data": data from document with document_id from collection
            }
        
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return None
    
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    
    docs = db.collection(collection).get()
    collection_data = []
    if len(docs) == 0:
        print('Collection not found: {}'.format(collection))
    for doc in docs:
        collection_data.append(
            {
                "document_id": doc.id,
                "data": doc.to_dict()
            }
        )
    return collection_data

def read_document_with_filter(atribut: str, op: str, value, collection: str) -> List[Dict]:
    """
    Args:
        atribut: str
            field_path for filter. Atribut at collection
        op: str
            op_string for filter. For example: "==", ">", "<", "in"
        value:
            value for filter. Atribut value
        collection: str
            name collection on cloud. Default=None: the name collection is taken from the firebase_config.yaml

    Returns:
         List[Dict] - list of dictinary:
            {
                "document_id": document id from collection
                "data": data from document with document_id from collection
            }
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return None
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)
    # Select document with filter
    db = firestore.client()
    docs = db.collection(collection).where(filter=FieldFilter(field_path=atribut,op_string=op, value=value)).get()
    # Write in List
    collection_data = []
    if len(docs) == 0 and len(db.collection(collection).get()) == 0:
        print('Not found {} collection on cloud'.format(collection))
    for doc in docs:
        collection_data.append(
            {
                "document_id": doc.id ,
                "data": doc.to_dict()
            }
        )
    return collection_data
    
def read_document(document_id: str, collection: str) -> Dict:
    """Read document with id in collection from Firebase

    Args:
        document_id: int
          document identificator
        collection: str
            name collection on cloud.

    Returns:
        List[Dict] - list of documents with document_id
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return None
        
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)
    # Select document with filter
    db = firestore.client()
    doc = db.collection(collection).document(document_id).get()
    if len(db.collection(collection).get()) == 0:
        print('Not found {} collection on cloud'.format(collection))
    if doc.exists:
        return doc.to_dict()
    else:
        print('Not found in {0} collection on cloud document {1} '.format(collection, document_id))
        return None

def add_document(new_data: Dict, collection: str) -> str:
    """Add document in collection from Firebase

    Args:
       new_data: Dict
          new data in document with id
       collection: str
          name collection on cloud.
    
    Return:
        str: id added document
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found collection name")
        return None
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    doc = db.collection(collection).add(new_data)
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)
    save_changing(
        name_function = "add_document",
        time_of_changing = time_of_changing,
        params = {
            "new_data": new_data,
            "collection": collection
        }
    )
    return doc[1].id



def update_document(document_id: str, new_data: Dict, collection: str):
    """Update document with id in collection from Firebase

    Args:
       id: int
          id document
       new_data: Dict
          new data in document with id
       collection: str
          name collection on cloud. Default: the name collection is taken from the firebase_config.yaml
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return

    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    docs = db.collection(collection).get()
    if len(docs) == 0:
        print('Collection not found: {}'.format(collection))
        return
    doc = db.collection(collection).document(document_id).get()
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)

    if doc.exists:
        save_changing(
            name_function = "update_document",
            time_of_changing = time_of_changing,
            params = {
               "document_id": document_id,
               "new_data": new_data,
               "collection": collection
            }
        )
        db.collection(collection).document(document_id).update(new_data)
    else:
        db.collection(collection).add(new_data)
    
    return

def update_document_array(document_id: str, array_name: str, value: List, collection: str = None):
    """Update document array with id in collection from Firebase

    Args:
        id: int
            id document
        array_name: str
            array name in collection
        collection: str
            name collection on cloud.
        value:
            new element for adding
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return

    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    docs = db.collection(collection).get()
    if len(docs) == 0:
        print('Collection not found: {}'.format(collection))
        return
    doc = db.collection(collection).document(document_id).get()
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)

    if doc.exists:
        save_changing(
            name_function = "update_document_array",
            time_of_changing = time_of_changing,
            params = {
               "document_id": document_id,
               "array_name": array_name,
               "collection": collection,
               "value": value
            }
        )
        db.collection(collection).document(document_id).update({array_name: firestore.ArrayUnion(value)})
    else:
        print("Error adding elements in array")
    
    return
    
def increment_value(document_id: str, atribut: str, value: List, collection: str = None):
    """Update document value with id in collection from Firebase

    Args:
        document_id: int
            id document
        atribut: str
            atribut name in collection
        collection: str
            name collection on cloud.
        value:
            increment value: new valut = current + value
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return

    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    docs = db.collection(collection).get()
    if len(docs) == 0:
        print('Collection not found: {}'.format(collection))
        return
    doc = db.collection(collection).document(document_id).get()
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)

    if doc.exists:
        save_changing(
            name_function = "increment_value",
            time_of_changing = time_of_changing,
            params = {
               "document_id": document_id,
               "atribut": atribut,
               "collection": collection,
               "value": value
            }
        )
        db.collection(collection).document(document_id).update({atribut: firestore.Increment(value)})
    else:
        print("Error increment")
    return
    
def delete_document(document_id: str, collection: str = None):
    """Delete document with id in collection from Firebase

    Args:
       document_id: int
          id document
       new_data: Dict
          new data in document with id
       collection: str
          name collection on cloud.
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return None
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    docs = db.collection(collection).get()
    if len(docs) == 0:
        print('Collection not found: {}'.format(collection))
        return
    db.collection(collection).document(document_id).delete()
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)
    save_changing(
        name_function = "delete_document",
        time_of_changing = time_of_changing,
        params = {
            "document_id": document_id,
            "collection": collection
        }
    )

def upload_file(path_local: str, path_on_cloud: str = None) -> str:
    """Upload file on Firbase storage.

    Args:
      path_local: str
          local path to the file to upload
      path_on_cloud: str
          path on cloud to the file

    Returns:
      path_on_cloud: str

    Raises:
      OSError: Could not open/read file.
      NameError: This file not exists.
      ConnectionError: Could not connection to firebase.
      RuntimeError: Could not upload file
    """
    firebase_config = get_config()

    if not os.path.exists(path_local):
        print("This file not exists: {}".format(path_local))
        return None
    
    try:
        # Initilization app
        firebase = pyrebase.initialize_app(firebase_config)
        storage = firebase.storage()
    except ConnectionError as exc:
        print('Failed to connection database')
        return None
        

    if path_on_cloud is None:
        # Create path from timestamp
        tz=timezone(firebase_config['timezone'])
        path_on_cloud = datetime.now(tz=tz).strftime("%Y-%m-%d_%H-%M-%S.jpg")

    # Upload file
    try:
        storage.child(path_on_cloud).put(path_local)
    except:
        raise RuntimeError("Error upload file on cloud")
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)
    save_changing(
        name_function = "upload_file",
        time_of_changing = time_of_changing,
        params = {
            "path_local": path_local,
            "path_on_cloud": path_on_cloud
        }
    )
    return path_on_cloud

def download_file(path_on_cloud: str, path_local: str = None) -> str:
    """Download file from Firbase storage.
  
    Args:
      path_on_cloud: str
          path on cloud to the file
      path_local: str
          local path to the file to download

    Returns:
      path_local: str

    Raises:
      OSError: Could not open/read file.
      NameError: This file exists yet.
      ConnectionError: Could not connection to firebase.
      RuntimeError: Could not upload file
    """
    firebase_config = get_config()

    if path_local is not None and os.path.exists(path_local):
        print("This file exists yet: {}".format(path_local))
        return None
    elif path_local is None:
        # Create path from timestamp
        tz=timezone(firebase_config['timezone'])
        path_local = datetime.now(tz=tz).strftime("%Y-%m-%d_%H-%M-%S.jpg")
    try:
        # Initilization app
        firebase = pyrebase.initialize_app(firebase_config)
        storage = firebase.storage()
    except ConnectionError as exc:
        print('Failed to connection database')
        return None
    
    all_files = storage.list_files()
    file_names = [file.name for file in all_files]
    if path_on_cloud not in file_names:
        print("This file not exists on cloud: {}".format(path_on_cloud))
        return None
    # Download file
    try:
        storage.child(path_on_cloud).download(path=path_on_cloud, filename=path_local)
    except ConnectionError as exc:
        print("Error download file from cloud")
        return None
    return path_local
    

def delete_file(path_on_cloud: str) -> str:
    """Delete file from Firbase storage.
  
    Args:
      path_on_cloud: str
          path on cloud to the file

    Raises:
      OSError: Could not open/read file.
      NameError: This file exists yet.
      ConnectionError: Could not connection to firebase.
      RuntimeError: Could not upload file
    """
    firebase_config = get_config()
    try:
        # Initilization app
        firebase = pyrebase.initialize_app(firebase_config)
        storage = firebase.storage()
    except ConnectionError as exc:
        print('Failed to connection database')
        return None
    
    all_files = storage.list_files()
    file_names = [file.name for file in all_files]
    if path_on_cloud not in file_names:
        print("This file not exists on cloud: {}".format(path_on_cloud))
        return None
    try:
        download_url = storage.child(path_on_cloud).get_url(None)
        storage.child(path_on_cloud).delete(name=path_on_cloud, token=download_url)
        tz=timezone(firebase_config['timezone'])
        time_of_changing = datetime.now(tz=tz)
        save_changing(
        name_function = "delete_file",
            time_of_changing = time_of_changing,
            params = {
            "path_on_cloud": path_on_cloud
            }
        )
    except ConnectionError as exc:
        print("Error delete file from cloud")
        return None
    
def add_farmer(data: Dict):
    '''Add farmer to firebase collection "farmers"'''
    add_document(add, "farmers")

def connect_farmer_to_agronomist(farmer_tg_id: int, agronomist_tg_id: int):
    '''
    Connect the farmer to the agronomist

    Args:
        farmer_tg_id: int
            farmer telegram identificator
        agronomist_tg_id: int
            agronomist telegram identificator
    '''
    # connect to firebase
    firebase_config = get_config()
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)
        
    # connect to collection "farmers" and check farmer exist
    db = firestore.client()
    collection = "farmers"
    docs = db.collection(collection).get()
    if len(docs) == 0:
        raise print('Collection not found: {}'.format(collection))
    
    docs = db.collection(collection).where(filter=FieldFilter(field_path="tg_id",op_string="==", value=farmer_tg_id)).get()
    if len(docs) == 0:
        raise print("Farmer with id {0} no exists in collection {1}".format(farmer_tg_id, collection))
    else:
        print(docs[0].to_dict())
        farmer_document_id = docs[0].id
    # connect to collection "agronomists" and check farmer exist
    db = firestore.client()
    collection = "agronomists"
    docs = db.collection(collection).get()
    if len(docs) == 0:
        raise print('Collection not found: {}'.format(collection))
    
    docs = db.collection(collection).where(filter=FieldFilter(field_path="tg_id",op_string="==", value=agronomist_tg_id)).get()
    if len(docs) == 0:
        raise print("Agronomist with id {0} no exists in collection {1}".format(agronomist_tg_id, collection))
    elif len(docs) == 1:
        
        data = docs[0].to_dict()
        if "available_farmers" in data:
            # add farmer to available_farmers
            farmers = data["available_farmers"]
            if farmer_document_id not in farmers:
                farmers.append(farmer_document_id)
        else:
            # create availeble_farmers with the farmer
            farmers = [farmer_document_id]
            
        data["available_farmers"] = farmers
        update_document(docs[0].id, data, "agronomists")
    else:
        raise print('So much document with agronomist with id {0} in collection {1}'.format(farmer_tg_id, collection))
    tz=timezone(firebase_config['timezone'])
    time_of_changing = datetime.now(tz=tz)
    save_changing(
        name_function = "connect_farmer_to_agronomist",
        time_of_changing = time_of_changing,
        params = {
            "farmer_tg_id": farmer_tg_id,
            "agronomist_tg_id": agronomist_tg_id
        }
    )
    
import time
def read_collection_with_composite_filter(collection: str, filters: List[Dict], order: Dict=None) -> List[Dict]:
    """Read collection with composite filter from Firebase
       
    Args:
        collection: str
            name collection on cloud.
        filters: List[Dict]
            list of filters
            [
                {
                    atribut: field_path for filter. Atribut at collection
                    op: op_string for filter. For example: "==", ">", "<", "in"
                    value: value for filter. Atribut value
                }
                ...
            ]
        order: Dict
            order by
            {
                atribut: field_path for filter. Atribut at collection
                desc: True or False
            }
    Returns:
        List[Dict] - list of dictinary:
            {
                "document_id": document id from collection
                "data": data from document with document_id from collection
            }
        
    """
    firebase_config = get_config()
    if collection is None:
        print("Not found the collection name")
        return None
    
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(firebase_config["serviceAccount"])
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    if len(filters) > 4 or len(filters) < 1:
        return None
    elif len(filters) == 4 and order is None:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).where(
        filter=FieldFilter(
            filters[2]["atribut"],
            filters[2]["op"],
            filters[2]["value"]
        )).where(filter=FieldFilter(
            filters[3]["atribut"],
            filters[3]["op"],
            filters[3]["value"]
        )).get()
    elif len(filters) == 3 and order is None:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).where(
        filter=FieldFilter(
            filters[2]["atribut"],
            filters[2]["op"],
            filters[2]["value"]
        )).get()
    elif len(filters) == 2 and order is None:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(
        filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).get()
    elif len(filters) == 1 and order is None:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).get()
    elif len(filters) == 4 and order["desc"]:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).where(
        filter=FieldFilter(
            filters[2]["atribut"],
            filters[2]["op"],
            filters[2]["value"]
        )).where(filter=FieldFilter(
            filters[3]["atribut"],
            filters[3]["op"],
            filters[3]["value"]
        )).order_by(order["atribut"], direction=firestore.Query.DESCENDING).get()
    elif len(filters) == 4:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).where(
        filter=FieldFilter(
            filters[2]["atribut"],
            filters[2]["op"],
            filters[2]["value"]
        )).where(filter=FieldFilter(
            filters[3]["atribut"],
            filters[3]["op"],
            filters[3]["value"]
        )).order_by(order["atribut"]).get()
    elif len(filters) == 3 and order["desc"]:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).where(
        filter=FieldFilter(
            filters[2]["atribut"],
            filters[2]["op"],
            filters[2]["value"]
        )).order_by(order["atribut"], direction=firestore.Query.DESCENDING).get()
    elif len(filters) == 3:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).where(
        filter=FieldFilter(
            filters[2]["atribut"],
            filters[2]["op"],
            filters[2]["value"]
        )).order_by(order["atribut"]).get()
    elif len(filters) == 2 and order["desc"]:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(
        filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).order_by(order["atribut"], direction=firestore.Query.DESCENDING).get()
    elif len(filters) == 2:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).where(
        filter=FieldFilter(
            filters[1]["atribut"],
            filters[1]["op"],
            filters[1]["value"]
        )).order_by(order["atribut"]).get()
    elif len(filters) == 1 and order["desc"]:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).order_by(order["atribut"], direction=firestore.Query.DESCENDING).get()
    elif len(filters) == 1:
        docs = db.collection(collection).where(filter=FieldFilter(
            filters[0]["atribut"],
            filters[0]["op"],
            filters[0]["value"]
        )).order_by(order["atribut"]).get()
    collection_data = []
    if len(docs) == 0:
        print('Collection not found: {}'.format(collection))
    for doc in docs:
        collection_data.append(
            {
                "document_id": doc.id,
                "data": doc.to_dict()
            }
        )
    return collection_data


def main():
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    data = read_document_with_filter(atribut = "tg_id", op = "==", value = 1200410322, collection = "agronomists")
    farmers_id = data[0]["data"]["available_farmers"]

    read_collection_with_composite_filter("calendar_events",
    [
        {
            "atribut": "type",
            "op": "==",
            "value": "task",
        },
        {
            "atribut": "status",
            "op": "==",
            "value": "a confirmation notification was sent to the agronomist",
        },
        {
            "atribut": "farmer_tg_id",
            "op": "in",
            "value": farmers_id,
        }],
        {
            "atribut": "timestamp_end",
            "desc": False
        }
    )
if __name__ == '__main__':
    main()
    
