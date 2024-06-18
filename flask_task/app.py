from flask import Flask, jsonify, request
from dotenv import load_dotenv
from os import getenv
from flask_apscheduler import APScheduler
import pymssql
import requests


app = Flask(__name__)
scheduler = APScheduler()
load_dotenv('env')


#Database Configuration
DB_NAME = getenv('DB_NAME')
DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_SERVER = getenv('DB_SERVER')
DB_PORT = getenv('DB_PORT')
DB_MASTER = getenv('DB_MASTER')


# Check if running in Docker environment
if getenv('DOCKER_ENV') == 'true':
    # If running in Docker, include port
    DB_SERVER += ','+DB_PORT


# # Wait for MSSQL server to be ready
# def wait_for_mssql():
#     max_retries = 10
#     retries = 0
#     while retries < max_retries:
#         try:
#             conn = pymssql.connect(server=DB_SERVER, user=DB_USER, password=DB_PASSWORD, database=DB_MASTER)
#             conn.close()
#             return True
#         except Exception as e:
#             print(f"Connection to MSSQL server failed. Retrying ({retries+1}/{max_retries})...")
#             retries += 1
#             time.sleep(5)  # Wait for 5 seconds before retrying
#     print("Max retries reached. Unable to connect to MSSQL server.")
#     return False


# # Wait for MSSQL server to be ready before starting the Flask app
# if not wait_for_mssql():
#     exit(1)


def create_database_and_table_if_not_exists():
    try:
        
        conn = pymssql.connect(server=DB_SERVER,port = DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_MASTER )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sys.databases WHERE name = 'WebsitesDB'")
        exists = cursor.fetchone()[0]
        if not exists:

            # Create Database
            conn.autocommit(True)
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE WebsitesDB")
            conn.autocommit(False)

            print('WebsitesDB created succesfully.')

            # Switch to WebsitesDB
            cursor.execute("USE WebsitesDB")


        else:
            print('WebsitesDB already exists.')

        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'Websites'")
        exists = cursor.fetchone()[0]
        if not exists:
            # Create websites table
            cursor.execute("""CREATE TABLE websites(\
                           id INT PRIMARY KEY IDENTITY (1,1),\
                           site_name VARCHAR(100),\
                           url VARCHAR(255),\
                           status VARCHAR(4)\
            )""")
            conn.commit()
            print('Websites table created successfully.')
        else:
            print('Websites table already exists.')

    except pymssql.Error as e:
        print(f"Error {e}")
        return False
    
    return True


if not create_database_and_table_if_not_exists():
    exit(1)
conn = pymssql.connect(server=DB_SERVER, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


def execute_query(query, params=None, fetchone=False, fetchall=False):
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = None
        conn.commit()
        return result
            

def check_status(url):
    new_status = 'DOWN'
    try:
        response = requests.get('https://' + url).status_code
        if 200 <= response < 300 :
            new_status = 'UP'
    except Exception as e:
        print('Error faced while requesting the url', e)
    return new_status


# Checking the status of the websites
def check_website_status():
    print('Scheduled job running')
    websites = execute_query('SELECT id, url, status FROM websites', fetchall=True)
    for website in websites:
        id, url, prev_status = website
        new_status = check_status(url)
        if prev_status != new_status:
            execute_query("UPDATE websites SET status = %s WHERE id = %s", (new_status, id))

    
# Scheduling the task to run check_website_status function after every 10 seconds
@scheduler.task('interval', id='check_website_status', seconds=10, misfire_grace_time=900)
def run_check_website_status():
    print(scheduler.get_jobs())
    check_website_status()



@app.route('/websites', methods=['POST'])
def create_websites():
    data = request.json
    status = check_status(data['url'])
    execute_query("INSERT INTO websites (site_name, url, status) VALUES (%s, %s, %s)", 
                   (data['site_name'], data['url'], status))
    return jsonify({'message': 'Websites created successfully'}), 201


@app.route('/website/status', methods=['GET'])
def all_website_status():
    websites = execute_query('SELECT site_name, url, status FROM websites', fetchall=True)
    all_websites_status_list = []
    if websites:
        for website in websites:
            temp_dict = {}
            temp_dict['url'] = website[1] 
            temp_dict['status'] = website[2] 
            temp_dict['site_name'] = website[0] 
            all_websites_status_list.append(temp_dict)
        return jsonify(response=all_websites_status_list), 200    
    
    return jsonify({"message":"No records found!"}), 404   


@app.route('/website/status/<site_name>', methods=['GET'])
def get_website_status(site_name):
    website = execute_query('SELECT site_name, url, status FROM websites WHERE site_name = %s', site_name, fetchone=True)
    if website:
        return jsonify({'site_name': website[0], 'url': website[1], 'status': website[2]}), 200
    return jsonify({'message':'No such site-name found!'}), 404


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000)
    scheduler.shutdown()
    conn.close()