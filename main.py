import time
import config
from etl_functions import extract_data, process_data, ingest_data
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')  # Set the templates folder

# Custom filter function to format the timestamp as 'yyyy-mm'
@app.template_filter('format_date')
def format_date(value):
    """
    Custom Flask template filter to format the timestamp as 'yyyy-mm'.

    Args:
        value (datetime): The timestamp value to be formatted.

    Returns:
        str: The formatted timestamp as 'yyyy-mm'.
    """
    return value.strftime('%Y-%m')


@app.route('/')
def index():
    """
    Flask route to handle the ETL pipeline.

    Returns:
        str: The rendered HTML template with the processed data.
    """
    # Define the start_time before executing the ETL pipeline
    start_time = time.time()

    last_extracted_timestamp = config.get_last_extracted_timestamp()

    if last_extracted_timestamp is None:
        print("No previous extraction found. Starting a fresh extraction.")
    else:
        print(f"Resuming from last extracted timestamp: {last_extracted_timestamp}")

    # Extract data from the GHO API and ingest it into the database
    extracted_data = extract_data(last_extracted_timestamp)

    if extracted_data:
        processed_data = process_data(extracted_data)
        if processed_data is not None and not processed_data.empty:
            ingest_data(processed_data)
            config.save_last_extracted_timestamp(processed_data['timestamp'].max())
        else:
            print("No new data to process or ingest.")

    # Convert processed_data DataFrame to a list of dictionaries
    data = processed_data.to_dict(orient='records') if processed_data is not None else []

    # Calculate the elapsed time for the ETL pipeline
    elapsed_time = time.time() - start_time
    print(f"ETL pipeline completed in {elapsed_time:.2f} seconds.")

    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
