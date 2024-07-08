import json
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from db import DatabaseManager
from logger import Logger as log

load_dotenv('./env_variables')

DB_TABLE_NAME = getenv('DB_TABLE_NAME')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)


# Configure database credentials by retrieving required variables from env_variables file
def configure_database():
    """
    Retrieve database configuration from the app's environment variables.
    """
    DB_NAME = getenv('DB_NAME')
    DB_USER = getenv('DB_USER')
    DB_PASSWORD = getenv('DB_PASSWORD')
    DB_SERVER = getenv('DB_SERVER')
    return DB_NAME, DB_USER, DB_PASSWORD, DB_SERVER


def establish_connection():
    """
    Establishes a connection to the database and returns the connection object.
    """
    DB_NAME, DB_USER, DB_PASSWORD, DB_SERVER = configure_database()
    return DatabaseManager(server=DB_SERVER, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


def execute_sql_query(query):
    """
    Execute an SQL query using the provided parameters and fetch options.
    """
    # Establish database connection
    with establish_connection() as sql_db:
        # Execute the query using DatabaseManager context
        output = sql_db.execute_query(query)
    
    return output
    

def get_table_columns():
    query = f"""
    SELECT COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = '{DB_TABLE_NAME}'
    """
    result = execute_sql_query(query)
    columns = [row[0] for row in result]
    return columns


def bulk_insert(df):
    columns = get_table_columns()
    known_columns = ['TICKER_ISIN', 'COST', 'QUANTITY', 'DATE']
    columns_to_insert = [col for col in columns if col not in known_columns]

    # Ensure columns to insert are set to None
    for col in columns_to_insert:
        df.loc[:, col] = None

    df = df[known_columns + columns_to_insert]
    
    # Convert DataFrame to list of tuples
    records = df.to_records(index=False)
 
    # Convert records to appropriate SQL values format
    def format_record(record):
        formatted_record = []
        for item in record:
            if isinstance(item, pd.Timestamp):
                formatted_record.append(f"'{item.strftime('%Y-%m-%d 00:00:00.000')}'")
            elif isinstance(item, np.float64):
                formatted_record.append(float(item))
            elif item is None:
                formatted_record.append("NULL")
            else:
                formatted_record.append(item)
        return tuple(formatted_record)

    # Convert DataFrame to list of tuples (records)
    records = [format_record(row) for row in df.to_numpy()]
    
    # Prepare SQL values for insertion
    values = ', '.join([str(record).replace("'NULL'", "NULL") for record in records])
    
    # Construct the insert query
    insert_query = f"""
    INSERT INTO {DB_TABLE_NAME} ({', '.join(known_columns + columns_to_insert)})
    VALUES {values}
    """
    print(insert_query)

    # Execute the insert query
    res = execute_sql_query(insert_query)
    return res


def bulk_update(df, date_today):
    responses = [] 

    # Establish database connection
    with establish_connection() as sql_db:
        # Update each record
        for _, row in df.iterrows():
            update_query = f"""
            UPDATE {DB_TABLE_NAME}
            SET COST={row['COST']}, QUANTITY={row['QUANTITY']}
            WHERE TICKER_ISIN='{row['TICKER_ISIN']}' AND DATE='{date_today}'
            """
            res = sql_db.execute_query(update_query)
            
            if isinstance(res, tuple) and res[0] == 'Error':
                responses.append({'query': 'UPDATE', 'status': 'failed', 'message':str(res[1])})
            else:
                responses.append({'query': 'UPDATE', 'status': 'success', 'message': f"Record for {row['TICKER_ISIN']} updated successfully."})
        
    return responses


def load_echo_fund(data):
    date_today = datetime.now().strftime("%Y-%m-%d 00:00:00.000")
    
    # Convert input data to DataFrame
    input_df =pd.DataFrame(data)

    # Add the 'DATE' column with today's date
    input_df['DATE'] = date_today
    
    # Get existing records from the database
    tickers = "','".join(input_df['TICKER_ISIN'].tolist())
    check_query = f"""
    SELECT TICKER_ISIN, COST, QUANTITY, DATE FROM {DB_TABLE_NAME}
    WHERE TICKER_ISIN in ('{tickers}') AND DATE='{date_today}'
    """

    existing_records = execute_sql_query(check_query)
    existing_df = pd.DataFrame(existing_records, columns=['TICKER_ISIN', 'COST', 'QUANTITY', 'DATE'])
     # Convert DATE column to string format before merge
    existing_df['DATE'] = pd.to_datetime(existing_df['DATE']).dt.strftime("%Y-%m-%d 00:00:00.000")
    
    # Merge input data with existing records
    merged_df = input_df.merge(existing_df, on=['TICKER_ISIN', 'DATE'], how='outer', suffixes=('', '_existing'), indicator=True)
    
    # Find new records (only in input_df)
    new_records = merged_df[merged_df['_merge'] == 'left_only'][input_df.columns]
    print("New Records:")
    print(new_records)
    
    responses = []

    if not new_records.empty:
        try:
            bulk_insert(new_records)
            responses.append({'query': 'INSERT', 'status': 'success', 'message': 'New records created successfully'})
        except Exception as e:
            responses.append({'query': 'INSERT', 'status': 'failed', 'message': str(e)})


    update_records = merged_df[merged_df['_merge'] == 'both']
    update_records = update_records[(update_records['COST'] != update_records['COST_existing']) | (update_records['QUANTITY'] != update_records['QUANTITY_existing'])]
    
    if not update_records.empty:
        try:
            update_responses = bulk_update(update_records, date_today)
            responses.extend(update_responses)
        except Exception as e:
            responses.append({'query': 'UPDATE', 'status': 'failed', 'message': str(e)})
    else:
        responses.append({'query': 'UPDATE', 'status': 'success', 'message': 'No updates found.'})
    
    log.info(json.dumps(responses, indent=4))
    if responses == []:
        responses ='No changes detected.'
    return responses
