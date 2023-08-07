import requests
import pandas as pd
import xml.etree.ElementTree as ET  # Import the ElementTree module
import psycopg2
import logging
import config
# Data extraction function
def extract_data(last_extracted_timestamp):
    # API URL and parameters with date filter
    api_url = f'https://apps.who.int/gho/athena/api/GHO/WHOSIS_000001?filter=COUNTRY:UGA&asof={last_extracted_timestamp}'

    # Make API request
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception if the response status is not 2xx
        root = ET.fromstring(response.text)
        data = root.find('Data')
        observations = data.findall('Observation')
        return observations
    except requests.exceptions.RequestException as e:
        logging.error("Error during data extraction:", exc_info=True)
        return None
    except Exception as err:
        logging.error("An unexpected error occurred during data extraction:", exc_info=True)
        return None

# Data processing function
def process_data(data):
    if data is None:
        return None

    # Process the XML data and convert it to a DataFrame
    rows = []
    for observation in data:
        timestamp = observation.find('Dim[@Category="YEAR"]').attrib['Code']
        country_code = observation.find('Dim[@Category="COUNTRY"]').attrib['Code']
        life_expectancy = float(observation.find('Value').attrib['Numeric'])

        # Add other columns from the XML data
        region = observation.find('Dim[@Category="REGION"]').attrib['Code']
        sex = observation.find('Dim[@Category="SEX"]').attrib['Code']

        rows.append({
            'timestamp': timestamp,
            'country_code': country_code,
            'life_expectancy': life_expectancy,
            'region': region,
            'sex': sex
        })

    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y')
    return df

# Data ingestion function
def ingest_data(dataframe):
    try:
        # Open a connection to the database
        conn = psycopg2.connect(config.DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Create a table for the data (if it doesn't exist)
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS life_expectancy_data (
            timestamp DATE,
            country_code VARCHAR(3),
            life_expectancy FLOAT
        );
        '''
        cursor.execute(create_table_query)

        # Insert data into the table
        for index, row in dataframe.iterrows():
            insert_query = f'''
            INSERT INTO life_expectancy_data (timestamp, country_code, life_expectancy)
            VALUES ('{row['timestamp']}', '{row['country_code']}', {row['life_expectancy']});
            '''
            cursor.execute(insert_query)

        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        print("Data ingestion completed.")
    except (Exception, psycopg2.Error) as error:
        logging.error("Error during data ingestion:", exc_info=True)

# Other utility functions for saving and retrieving the last extracted timestamp
# in the `config.py` file.

