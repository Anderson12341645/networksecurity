import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

import certifi
import pandas as pd
import pymongo
from networksecurity.exception.exception import NetworkSecurityException  # Fixed case
from networksecurity.logging.logger import logging

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ca = certifi.where()

class NetworkDataExtract:
    def __init__(self):
        pass  # No need for try/except if empty

    def csv_to_json_convertor(self, file_path):  # Fixed method name
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)  # True not true
            records = data.to_dict(orient='records')  # Correct conversion
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)  # Add SSL
            db = client[database]
            col = db[collection]
            result = col.insert_many(records)
            return len(result.inserted_ids)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == '__main__':
    FILE_PATH = r"network_data\phisingData.csv"  # Raw string
    DATABASE = "AndersonAI"
    COLLECTION = "NetworkData"
    
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)  # Capture return
    print(f"Converted records: {len(records)}")
    
    no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)
    print(f"Inserted records: {no_of_records}")