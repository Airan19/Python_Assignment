from flask import jsonify, request, current_app as app, Blueprint
from main import scheduler
from db import DatabaseManager
import requests
import config
from logger import Logger

web_api_bp = Blueprint('web_api', __name__)
log = Logger()


def execute_sql_query(query, params=None, fetchone=False, fetchall=False):
    configs = config.get_configs(app)
    server = configs['DB_SERVER']
    user = configs['DB_USER']
    password = configs['DB_PASSWORD']
    database = configs['DB_NAME']
    main_db = configs['DB_MASTER']

    with DatabaseManager(server, user, password, database, main_db) as sql_db:
        output = sql_db.execute_query(query, params,fetchone, fetchall)
        return output
    

def check_status(url):
    new_status = 'DOWN'
    try:
        response = requests.get('https://' + url).status_code
        if 200 <= response < 300 :
            new_status = 'UP'
    except Exception as e:
        log.error('Error faced while requesting the url', e)
    return new_status


# Checking the status of the websites
def check_website_status():
    log.info('Scheduled job running')
    websites = execute_sql_query('SELECT id, url, status FROM websites', fetchall=True)
    for website in websites:
        id, url, prev_status = website
        new_status = check_status(url)
        if prev_status != new_status:
            execute_sql_query("UPDATE websites SET status = %s WHERE id = %s", (new_status, id))


# Scheduling the task to run check_website_status function after every 10 seconds
@scheduler.task('interval', id='check_website_status', seconds=10, misfire_grace_time=900)
def run_check_website_status():
    check_website_status()


@web_api_bp.route('/websites', methods=['POST'])
def create_websites():
    data = request.json
    status = check_status(data['url'])
    execute_sql_query("INSERT INTO websites (site_name, url, status) VALUES (%s, %s, %s)", 
                   (data['site_name'], data['url'], status))
    return jsonify({'message': 'Websites created successfully'}), 201


@web_api_bp.route('/website/status', methods=['GET'])
def all_website_status():
    websites = execute_sql_query('SELECT site_name, url, status FROM websites', fetchall=True)
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


@web_api_bp.route('/website/status/<site_name>', methods=['GET'])
def get_website_status(site_name):
    website = execute_sql_query('SELECT site_name, url, status FROM websites WHERE site_name = %s', site_name, fetchone=True)
    if website:
        return jsonify({'site_name': website[0], 'url': website[1], 'status': website[2]}), 200
    return jsonify({'message':'No such site-name found!'}), 404
