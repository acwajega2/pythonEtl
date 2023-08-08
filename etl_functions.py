import requests
import pandas as pd
import xml.etree.ElementTree as ET
import psycopg2
import logging
import config

def extract_data(last_extracted_timestamp):
    api_url = f'https://apps.who.int/gho/athena/api/GHO/WHOSIS_000001?filter=COUNTRY:UGA&asof={last_extracted_timestamp}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        data = root.find('Data')
        if data is None:
            logging.error("Unexpected data structure received from the API.")
            return None

        observations = data.findall('Observation')
        return observations
    except requests.exceptions.RequestException as e:
        logging.error("Error during API request:", exc_info=True)
        return None
    except Exception as err:
        logging.error("An unexpected error occurred during data extraction:", exc_info=True)
        return None

def process_data(data):
    if data is None:
        return None

    rows = []
    for observation in data:
        timestamp = observation.find('Dim[@Category="YEAR"]').attrib['Code']
        country_code = observation.find('Dim[@Category="COUNTRY"]').attrib['Code']
        life_expectancy = float(observation.find('Value').attrib['Numeric'])
        region = observation.find('Dim[@Category="REGION"]').attrib['Code']
        sex = observation.find('Dim[@Category="SEX"]').attrib['Code']

        rows.append({
            'timestamp': timestamp,
            'country_code': country_code,
            'region': region,
            'sex': sex,
            'life_expectancy': life_expectancy
        })

    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y')
    return df

def ingest_data(dataframe):
    try:
        conn = psycopg2.connect(config.DB_CONNECTION_STRING)
        cursor = conn.cursor()

        create_table_query = '''
    CREATE TABLE IF NOT EXISTS life_expectancy_data (
        timestamp DATE PRIMARY KEY,
        country_code VARCHAR(3),
        sex VARCHAR(10),
        region VARCHAR(10),
        life_expectancy FLOAT
    );
'''
        cursor.execute(create_table_query)

        # Convert DataFrame to a list of tuples for bulk insert
        data_to_insert = [tuple(row) for row in dataframe.to_numpy()]

        # Use cursor.executemany to perform bulk insert or update
        insert_query = '''
        INSERT INTO life_expectancy_data (timestamp, country_code, sex, region, life_expectancy)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (timestamp) DO UPDATE
        SET sex = EXCLUDED.sex, region = EXCLUDED.region, life_expectancy = EXCLUDED.life_expectancy;
        '''
        cursor.executemany(insert_query, data_to_insert)

        conn.commit()
        cursor.close()
        conn.close()
        print("Data ingestion completed.")
    except (Exception, psycopg2.Error) as error:
        logging.error("Error during data ingestion:", exc_info=True)

def extract_and_process_data(last_extracted_timestamp):
    extracted_data = extract_data(last_extracted_timestamp)

    if extracted_data:
        processed_data = process_data(extracted_data)
        return processed_data
    else:
        return None
