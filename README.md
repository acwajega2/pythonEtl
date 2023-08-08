# WHO GHO ETL Pipeline and Flask Web Application

This repository contains an ETL pipeline that extracts life expectancy data from the WHO Global Health Observatory (GHO) OData API, processes the data, and ingests it into a PostgreSQL database. Additionally, it includes a Flask web application to visualize the life expectancy data.

## Setup Instructions

1. **Install Dependencies:**
   - Make sure you have Python 3.x installed.
   - Install the required Python packages by running: `pip install requests pandas psycopg2 Flask`

2. **Setup PostgreSQL Database:**
   - Create a PostgreSQL database with the name `etl_db`.
   - Make sure you have a PostgreSQL server running with the necessary credentials (`user=postgres`, `password=postgres`, `host=127.0.0.1`).
   - Update the `DB_CONNECTION_STRING` variable in `config.py` with your PostgreSQL database credentials. Example: `postgresql://user:password@localhost:5432/etl_db`

3. **Clone the Repository:**
   - Clone this repository to your local machine.

4. **Run the ETL Pipeline:**
   - Open a terminal and navigate to the repository directory.
   - Execute the ETL pipeline using the following command: `python main.py`

5. **Run the Flask Web Application:**
   - Once the ETL pipeline is completed, you can run the Flask web application.
   - In the terminal, execute the following command: `python main.py`
   - The Flask app will start, and you can access it in your web browser at `http://127.0.0.1:5000/` or `http://localhost:5000/`.

## Additional Notes

- The ETL pipeline can be stopped and resumed using the last extracted timestamp, stored in the `last_extracted_timestamp.json` file. This feature allows the pipeline to pick up from the last successful extraction point in case of interruptions or resuming on subsequent runs.
- Data validation and error handling have been implemented in the code to handle unexpected scenarios gracefully. In case of errors, check the logs in the terminal for error messages and consider enhancing the error handling in the code.
- The ETL pipeline includes unit tests to verify the functionality of individual functions and the pipeline as a whole. The unit tests can be found in the `test_etl_functions.py` file.
- The pipeline efficiently fetches only the most recent data from the WHO GHO API by using the `last_extracted_timestamp` parameter in the API query.
- The PostgreSQL database table, `life_expectancy_data`, has been configured with a primary key constraint on `timestamp`, `region`, `country_code`, and `life_expectancy`. This ensures that duplicate records are prevented, and records are updated if they already exist in the database based on these unique constraints.

- The Flask web application uses the `index.html` template located in the `templates` folder to render the life expectancy data. The data is passed to the template as a list of dictionaries and displayed using Jinja templating.

