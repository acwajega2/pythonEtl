import time
import config
from etl_functions import extract_data, process_data, ingest_data

def main():
    # Initialize the ETL pipeline
    start_time = time.time()

    # Fetch the last extracted timestamp from the database or a file
    last_extracted_timestamp = config.get_last_extracted_timestamp()

    # Extract data from the GHO OData API
    extracted_data = extract_data(last_extracted_timestamp)

    if extracted_data:
        # Process the data
        processed_data = process_data(extracted_data)

        # Ingest data into PostgreSQL
        ingest_data(processed_data)

        # Save the latest extracted timestamp for resumability
        config.save_last_extracted_timestamp(processed_data['timestamp'].max())

    # Finalize the ETL pipeline
    elapsed_time = time.time() - start_time
    print(f"ETL pipeline completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
