import json
from os import getenv
from db import DatabaseManager
from flask import request, jsonify, Blueprint
from dotenv import load_dotenv
from datetime import datetime
from logger import Logger as log

load_dotenv('./env_variables')

api_bp = Blueprint('api_bp', __name__)
DB_TABLE_NAME = getenv('DB_TABLE_NAME')

# Configure database credentials by retrieving required varaibles from env_variables file
def configure_database():
    """
    Retrieve database configuration from the app's environment variables.
    """
    DB_NAME = getenv('DB_NAME')
    DB_USER = getenv('DB_USER')
    DB_PASSWORD = getenv('DB_PASSWORD')
    DB_SERVER = getenv('DB_SERVER')
    return DB_NAME, DB_USER, DB_PASSWORD, DB_SERVER


def execute_sql_query(query):
    """
    Execute an SQL query using the provided parameters and fetch options.
    """
    DB_NAME, DB_USER, DB_PASSWORD, DB_SERVER = configure_database()
    
    # Execute the query using DatabaseManager context
    with DatabaseManager(server=DB_SERVER, user=DB_USER, password=DB_PASSWORD, 
                         database=DB_NAME) as sql_db:
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


@api_bp.route('/loadEchoFund', methods=['POST'])
def create_update_record():
    data = request.get_json()
    date_today = datetime.now().strftime('%Y-%m-%d 00:00:00.000')

    columns = get_table_columns()
    known_columns = ['TICKER_ISIN', 'COST', 'QUANTITY', 'DATE']
    columns_to_insert = [col for col in columns if col not in known_columns]
    responses = []

    for i in range(len(data.get('TICKER_ISIN', []))):
        ticker = data['TICKER_ISIN'][i]
        cost = data['COST'][i]
        quantity = data['QUANTITY'][i]

        # Check if record exists for today's date
        check_query = f"""SELECT COST, QUANTITY FROM {DB_TABLE_NAME} 
                        WHERE TICKER_ISIN='{ticker}' AND DATE='{date_today}'"""
        result = execute_sql_query(check_query)

        # if isinstance(result, tuple) and result[0] == 'Error':
        #     return jsonify([{'status': 'failed', 'message': str(result[1])}]), 500

        if len(result) == 0:
            # Insert new record if no records exist
            columns_str = ', '.join(['TICKER_ISIN', 'COST', 'QUANTITY', 'DATE'] + columns_to_insert)
            values_str = ', '.join([f"'{ticker}'", f"'{cost}'", f"'{quantity}'", f"'{date_today}'"] + ["NULL"] * len(columns_to_insert))

            insert_query = f"""
            INSERT INTO {DB_TABLE_NAME} ({columns_str})
            VALUES ({values_str})
            """
            res = execute_sql_query(insert_query)
            if isinstance(res, tuple) and res[0] == 'Error':
                responses.append({'status': 'failed', 'message': str(res[1])})
            else:
                responses.append({'status': 'success', 'message': f'Record for {ticker} created successfully'})

        else:
            existing_cost, existing_quantity = result[0]
            if existing_cost != cost or existing_quantity != quantity:
                # Update existing record if values differ
                update_query = f"""
                UPDATE {DB_TABLE_NAME}
                SET COST={cost}, QUANTITY={quantity}
                WHERE TICKER_ISIN='{ticker}' AND DATE='{date_today}'
                """
                res = execute_sql_query(update_query)
                if isinstance(res, tuple) and res[0] == 'Error':
                    responses.append({'status': 'failed', 'message': str(res[1])})
                else:
                    responses.append({'status': 'success', 'message': f'Record for {ticker} updated successfully'})
    log.info(json.dumps(responses, indent=4))
    return jsonify({'status': 'success', 'message': 'Records for created successfully'}), 200