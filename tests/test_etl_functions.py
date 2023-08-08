import unittest
import datetime
import pandas as pd
from unittest.mock import patch, MagicMock
import etl_functions

class TestETLFunctions(unittest.TestCase):

    def setUp(self):
        # Mock response text for API data
        self.mock_response_text = '''<?xml version="1.0" encoding="utf-8"?>
        <Data><Observation><Dim Category="YEAR" Code="2023"/><Dim Category="COUNTRY" Code="UGA"/>
        <Dim Category="REGION" Code="AFR"/><Dim Category="SEX" Code="BTSX"/><Value Numeric="65.0"/>
        </Observation></Data>'''

    def test_process_data(self):
        # Extract and process data
        data = etl_functions.extract_data(datetime.datetime(2022, 1, 1))
        df = etl_functions.process_data(data)

        # Check if the DataFrame is not None and has the expected number of columns
        self.assertIsNotNone(df)
        self.assertEqual(df.shape[1], 5)

    def test_ingest_data(self):
        # Create a sample DataFrame to test data ingestion
        df = pd.DataFrame({
            'timestamp': [datetime.datetime(2023, 1, 1)],
            'country_code': ['UGA'],
            'region': ['AFR'],
            'sex': ['BTSX'],
            'life_expectancy': [65.0]
        })

        # Mock the database connection and cursor
        with patch('etl_functions.psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Call the data ingestion function
            etl_functions.ingest_data(df)

            # Verify that the necessary database operations were called
            mock_connect.assert_called_once_with(etl_functions.config.DB_CONNECTION_STRING)
            mock_cursor.execute.assert_called_once()
            mock_cursor.executemany.assert_called_once()
            mock_conn.commit.assert_called_once()
            mock_cursor.close.assert_called_once()
            mock_conn.close.assert_called_once()

    def test_extract_and_process_data_with_valid_data(self):
        # Mock the extract_data and process_data functions
        last_extracted_timestamp = datetime.datetime(2022, 1, 1)
        with patch('etl_functions.extract_data') as mock_extract_data:
            with patch('etl_functions.process_data') as mock_process_data:
                # Set the return values for the mock functions
                mock_extract_data.return_value = [MagicMock()]
                mock_process_data.return_value = pd.DataFrame({
                    'timestamp': [datetime.datetime(2023, 1, 1)],
                    'country_code': ['UGA'],
                    'region': ['AFR'],
                    'sex': ['BTSX'],
                    'life_expectancy': [65.0]
                })

                # Call the extract_and_process_data function
                processed_data = etl_functions.extract_and_process_data(last_extracted_timestamp)

                # Verify that the necessary functions were called and the processed data is as expected
                mock_extract_data.assert_called_once_with(last_extracted_timestamp)
                mock_process_data.assert_called_once()
                self.assertIsNotNone(processed_data)
                self.assertEqual(processed_data.shape[0], 1)
                self.assertEqual(processed_data.shape[1], 5)

if __name__ == '__main__':
    unittest.main()
