import os
import json
import logging
import pandas as pd

DB_CONNECTION_STRING = "dbname=etl_db user=postgres password=postgres host=127.0.0.1"
TIMESTAMP_FILE_PATH = "last_extracted_timestamp.json"  # Path to the file storing the last extracted timestamp

def get_last_extracted_timestamp():
    try:
        if os.path.exists(TIMESTAMP_FILE_PATH):
            with open(TIMESTAMP_FILE_PATH, "r") as file:
                timestamp_data = json.load(file)
                return pd.to_datetime(timestamp_data.get("timestamp"))
    except Exception as e:
        logging.error("Error while retrieving last extracted timestamp:", exc_info=True)

    return None

def save_last_extracted_timestamp(timestamp):
    try:
        timestamp_data = {"timestamp": str(timestamp)}
        with open(TIMESTAMP_FILE_PATH, "w") as file:
            json.dump(timestamp_data, file)
    except Exception as e:
        logging.error("Error while saving last extracted timestamp:", exc_info=True)
